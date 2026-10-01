"""Online editing on a read-only host: catalog, images and embeddings kept
in Upstash. Driven with a dict-backed fake client, no network."""

import io
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.adapters.outbound.persistence.json_project_repository import JsonProjectRepository
from app.adapters.outbound.persistence.upstash_image_store import UpstashImageStore
from app.adapters.outbound.persistence.upstash_project_repository import UpstashProjectRepository
from app.adapters.outbound.rag.embedding_cache import CachedEmbedder
from app.adapters.outbound.rag.upstash_vector_cache import UpstashVectorCache
from app.domain.models import Project
from app.domain.services.project_service import ProjectService
from app.main import app

client = TestClient(app)


class FakeUpstash:
    def __init__(self) -> None:
        self.data: dict = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

    def hmget(self, key, fields):
        bucket = self.data.get(key, {})
        return [bucket.get(field) for field in fields]

    def hset(self, key, mapping):
        self.data.setdefault(key, {}).update(mapping)


def project(id_: str, title: str = "Titre") -> Project:
    text = {"fr": title, "en": title}
    return Project(id=id_, meta=text, title=text, result=text, problem=text, method=text, stack="Python", metrics=text)


def png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (40, 30), "teal").save(buffer, format="PNG")
    return buffer.getvalue()


# --- catalog -------------------------------------------------------------


def test_catalog_falls_back_to_the_shipped_one_until_first_save() -> None:
    repo = UpstashProjectRepository(FakeUpstash(), seed=JsonProjectRepository())
    assert [p.id for p in repo.list_all()] == [p.id for p in JsonProjectRepository().list_all()]


def test_saved_catalog_is_read_back_with_ids_assigned() -> None:
    repo = UpstashProjectRepository(FakeUpstash(), seed=JsonProjectRepository())
    saved = repo.replace_all([project("", "Détection d'objets")])
    assert saved[0].id == "detection-d-objets"
    assert repo.list_all() == saved


# --- images --------------------------------------------------------------


def test_uploaded_image_round_trips_as_webp(tmp_path: Path) -> None:
    store = UpstashImageStore(FakeUpstash(), seed_dir=tmp_path)
    url = store.save(png())
    content = store.load(url.rsplit("/", 1)[1])
    assert content is not None and content[8:12] == b"WEBP"


def test_shipped_images_are_served_from_disk(tmp_path: Path) -> None:
    name = "0" * 32 + ".webp"
    (tmp_path / name).write_bytes(b"shipped")
    assert UpstashImageStore(FakeUpstash(), seed_dir=tmp_path).load(name) == b"shipped"


def test_crafted_image_names_are_refused(tmp_path: Path) -> None:
    store = UpstashImageStore(FakeUpstash(), seed_dir=tmp_path)
    assert store.load("../../.env") is None
    assert store.load("projects.json") is None


def test_uploads_route_serves_images_with_a_long_cache() -> None:
    shipped = JsonProjectRepository().list_all()[0].image_url
    res = client.get(shipped)
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/webp"
    assert "immutable" in res.headers["cache-control"]
    assert client.get("/api/uploads/" + "f" * 32 + ".webp").status_code == 404


# --- embeddings ------------------------------------------------------------


class CountingEmbedder:
    def __init__(self) -> None:
        self.calls = 0

    def embed_documents(self, texts):
        self.calls += len(texts)
        return [[1.0, 0.0] for _ in texts]

    def embed_query(self, text):
        return [1.0, 0.0]


def test_a_passage_is_embedded_once_across_instances(tmp_path: Path) -> None:
    shared = UpstashVectorCache(FakeUpstash())
    api = CountingEmbedder()
    first = CachedEmbedder(api, "m", 2, path=tmp_path / "none.json", shared=shared)
    second = CachedEmbedder(api, "m", 2, path=tmp_path / "none.json", shared=shared)

    first.embed_documents(["nouveau projet"])
    second.embed_documents(["nouveau projet"])
    assert api.calls == 1


# --- index freshness --------------------------------------------------------


class RecordingRetriever:
    def __init__(self) -> None:
        self.indexes = 0

    def index(self, lang, chunks, source):
        self.indexes += 1

    def prune(self, lang, source, keep_ids):
        pass

    def search(self, query, lang, top_k):
        return []


class NoImages:
    def save(self, content):
        raise NotImplementedError

    def load(self, name):
        return None


def test_an_instance_reindexes_only_when_the_catalog_changed() -> None:
    repo = UpstashProjectRepository(FakeUpstash(), seed=JsonProjectRepository())
    retriever = RecordingRetriever()
    service = ProjectService(repo, NoImages(), retriever)

    service.sync_index()
    after_start = retriever.indexes
    service.sync_if_changed()
    assert retriever.indexes == after_start

    # Another instance saves the catalog: this one notices on its next question.
    UpstashProjectRepository(repo._client, seed=JsonProjectRepository()).replace_all([project("p1")])
    service.sync_if_changed()
    assert retriever.indexes > after_start


def test_catalog_is_editable_on_vercel_once_upstash_is_configured(offline_container, monkeypatch) -> None:
    monkeypatch.setenv("VERCEL", "1")
    assert offline_container.projects_editable is False
    offline_container.settings.upstash_redis_rest_url = "https://example.upstash.io"
    offline_container.settings.upstash_redis_rest_token = "token"
    offline_container.__dict__.pop("upstash", None)
    assert offline_container.projects_editable is True
