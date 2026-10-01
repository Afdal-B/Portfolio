from pathlib import Path

import pytest

from app.adapters.outbound.rag.embedding_cache import (
    DEFAULT_CACHE_PATH,
    CachedEmbedder,
    cache_key,
    read_cache,
    write_cache,
)
from app.config import Settings
from app.container import Container


class CountingEmbedder:
    def __init__(self) -> None:
        self.documents: list[str] = []
        self.queries: list[str] = []

    def embed_documents(self, texts):
        self.documents.extend(texts)
        return [[0.0, 1.0] for _ in texts]

    def embed_query(self, text):
        self.queries.append(text)
        return [1.0, 0.0]


def cached(tmp_path: Path, vectors: dict, model: str = "m", dimensions: int = 2):
    path = tmp_path / "embeddings.json"
    write_cache(path, model, dimensions, vectors)
    inner = CountingEmbedder()
    return CachedEmbedder(inner, "m", 2, path=path), inner


def test_cached_passages_need_no_api_call(tmp_path) -> None:
    embedder, inner = cached(tmp_path, {cache_key("m", 2, "RETRIEVAL_DOCUMENT", "a"): [0.6, 0.8]})
    assert embedder.embed_documents(["a"]) == [[0.6, 0.8]]
    assert inner.documents == []


def test_unknown_passages_are_embedded_live(tmp_path) -> None:
    embedder, inner = cached(tmp_path, {cache_key("m", 2, "RETRIEVAL_DOCUMENT", "a"): [0.6, 0.8]})
    assert embedder.embed_documents(["a", "b"]) == [[0.6, 0.8], [0.0, 1.0]]
    assert inner.documents == ["b"]


def test_queries_always_go_to_the_api(tmp_path) -> None:
    embedder, inner = cached(tmp_path, {})
    embedder.embed_query("q")
    assert inner.queries == ["q"]


def test_cache_from_another_model_is_ignored(tmp_path) -> None:
    path = tmp_path / "embeddings.json"
    write_cache(path, "autre-modele", 2, {"k": [1.0, 0.0]})
    assert read_cache(path, "m", 2) == {}


def test_shipped_cache_covers_every_indexed_passage() -> None:
    """Fails when a document or the project catalog changed without
    `make embeddings`: deployed instances would then embed those passages
    live at every cold start, against a quota of 100 per minute."""
    settings = Settings(gemini_api_key=None, admin_password=None)
    vectors = read_cache(DEFAULT_CACHE_PATH, settings.embedding_model, settings.embedding_dimensions)
    missing = [
        chunk.source_label
        for chunk in Container(settings).indexed_chunks()
        if cache_key(settings.embedding_model, settings.embedding_dimensions, "RETRIEVAL_DOCUMENT", chunk.text)
        not in vectors
    ]
    if missing:
        pytest.fail(f"Run `make embeddings`; not in the cache: {sorted(set(missing))}")
