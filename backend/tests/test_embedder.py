"""Gemini embedder, driven with a fake client: no network."""

from types import SimpleNamespace

from app.adapters.outbound.rag.embedder import GeminiEmbedder


class FakeModels:
    def __init__(self) -> None:
        self.calls: list[tuple[int, str]] = []

    def embed_content(self, model, contents, config):
        self.calls.append((len(contents), config.task_type))
        return SimpleNamespace(embeddings=[SimpleNamespace(values=[3.0, 4.0]) for _ in contents])


def build() -> tuple[GeminiEmbedder, FakeModels]:
    models = FakeModels()
    embedder = GeminiEmbedder("key", "gemini-embedding-001", 768, client=SimpleNamespace(models=models))
    return embedder, models


def test_documents_and_queries_use_their_own_task_type() -> None:
    embedder, models = build()
    embedder.embed_documents(["a", "b"])
    embedder.embed_query("q")
    assert models.calls == [(2, "RETRIEVAL_DOCUMENT"), (1, "RETRIEVAL_QUERY")]


def test_vectors_are_normalized() -> None:
    embedder, _ = build()
    assert embedder.embed_query("q") == [0.6, 0.8]


def test_large_inputs_are_split_into_api_sized_batches() -> None:
    embedder, models = build()
    vectors = embedder.embed_documents([str(i) for i in range(250)])
    assert len(vectors) == 250
    assert [size for size, _ in models.calls] == [100, 100, 50]
