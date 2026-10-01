"""Admin API, driven through HTTP with the project service overridden to use
a temp JSON file and a fake retriever."""

import json

import pytest
from fastapi.testclient import TestClient

from app.adapters.inbound.http.dependencies import get_project_service
from app.adapters.outbound.persistence.json_project_repository import JsonProjectRepository
from app.domain.services.project_service import ProjectService
from app.main import app

client = TestClient(app)

PASSWORD = "test-admin-password"

SAMPLE = {
    "meta": {"fr": "NLP", "en": "NLP"},
    "title": {"fr": "Nouveau projet", "en": "New project"},
    "result": {"fr": "Résultat", "en": "Result"},
    "problem": {"fr": "Problème", "en": "Problem"},
    "method": {"fr": "Méthode", "en": "Method"},
    "stack": "Python",
    "metrics": {"fr": "Métriques", "en": "Metrics"},
    "url": "#",
    "image_url": "",
    "screenshots": [],
    "image_seed": "afdal-9",
}


class RecordingRetriever:
    def __init__(self) -> None:
        self.indexed: list[tuple] = []
        self.pruned: list[tuple] = []

    def search(self, query, lang, top_k):
        return []

    def index(self, lang, chunks, source):
        self.indexed.append((lang, list(chunks), source))

    def prune(self, lang, source, keep_ids):
        self.pruned.append((lang, source, list(keep_ids)))


class StubImageStore:
    def save(self, content: bytes) -> str:
        return "/api/uploads/stub.webp"


@pytest.fixture
def admin(tmp_path, offline_container):
    offline_container.settings.admin_password = PASSWORD

    path = tmp_path / "projects.json"
    path.write_text("[]", encoding="utf-8")
    retriever = RecordingRetriever()
    service = ProjectService(
        repository=JsonProjectRepository(path), image_store=StubImageStore(), retriever=retriever
    )
    app.dependency_overrides[get_project_service] = lambda: service

    yield {"path": path, "retriever": retriever}

    app.dependency_overrides.clear()


def auth(password: str = PASSWORD) -> dict[str, str]:
    return {"Authorization": f"Bearer {password}"}


def test_requires_credentials(admin) -> None:
    assert client.get("/api/admin/projects").status_code == 401
    assert client.get("/api/admin/projects", headers=auth("wrong")).status_code == 401


def test_disabled_admin_looks_like_an_unknown_route(admin, offline_container) -> None:
    offline_container.settings.admin_password = None
    res = client.get("/api/admin/projects", headers=auth())
    assert res.status_code == 404
    assert res.json() == client.get("/api/does-not-exist").json()


def test_put_persists_to_json_and_assigns_ids(admin) -> None:
    res = client.put("/api/admin/projects", json=[SAMPLE], headers=auth())
    assert res.status_code == 200

    saved = res.json()
    assert len(saved) == 1
    assert saved[0]["id"] == "nouveau-projet"  # slugified from the FR title

    on_disk = json.loads(admin["path"].read_text(encoding="utf-8"))
    assert on_disk[0]["title"]["fr"] == "Nouveau projet"


def test_put_keeps_existing_ids_and_order(admin) -> None:
    first = client.put("/api/admin/projects", json=[SAMPLE], headers=auth()).json()
    second = {**SAMPLE, "title": {"fr": "Deuxième", "en": "Second"}}

    res = client.put("/api/admin/projects", json=[second, first[0]], headers=auth()).json()

    assert [p["id"] for p in res] == ["deuxieme", "nouveau-projet"]


def test_put_reindexes_projects_in_both_languages(admin) -> None:
    client.put("/api/admin/projects", json=[SAMPLE], headers=auth())

    langs = [lang for lang, _chunks, _source in admin["retriever"].indexed]
    assert langs == ["fr", "en"]

    _lang, chunks, source = admin["retriever"].indexed[0]
    assert source == "admin_project"
    assert chunks[0].id == "fr-admin-project-nouveau-projet"
    assert "Nouveau projet" in chunks[0].text


def test_deleting_a_project_persists_and_prunes_its_chunks(admin) -> None:
    client.put("/api/admin/projects", json=[SAMPLE], headers=auth())
    res = client.put("/api/admin/projects", json=[], headers=auth())

    assert res.json() == []
    assert json.loads(admin["path"].read_text(encoding="utf-8")) == []
    # Last prune round keeps nothing, so the stale chunks get dropped.
    assert admin["retriever"].pruned[-1] == ("en", "admin_project", [])


def test_public_content_endpoint_reflects_admin_changes(admin) -> None:
    client.put("/api/admin/projects", json=[SAMPLE], headers=auth())

    public = client.get("/api/content/projects", params={"lang": "fr"}).json()

    assert len(public) == 1
    assert public[0]["title"] == "Nouveau projet"
