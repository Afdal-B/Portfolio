"""In-memory retriever, driven with a fake embedder: no network."""

from app.adapters.outbound.rag.memory_retriever import InMemoryRetriever
from app.domain.models import Chunk


class FakeKnowledge:
    def __init__(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks
        self.calls = 0

    def chunks(self, lang):
        self.calls += 1
        return self._chunks


class FakeEmbedder:
    """Maps known texts to fixed vectors so ranking is deterministic."""

    def __init__(self, vectors: dict[str, list[float]]) -> None:
        self._vectors = vectors
        self.batches: list[int] = []

    def embed_documents(self, texts):
        self.batches.append(len(texts))
        return [self._vectors[text] for text in texts]

    def embed_query(self, text):
        self.batches.append(1)
        return self._vectors[text]


def chunk(id_: str, text: str, label: str, category: str = "profile") -> Chunk:
    return Chunk(id=id_, lang="fr", category=category, text=text, source_label=label)


def build(knowledge_chunks, vectors):
    knowledge = FakeKnowledge(knowledge_chunks)
    embedder = FakeEmbedder(vectors)
    retriever = InMemoryRetriever(knowledge=knowledge, embedder=embedder)
    return retriever, knowledge, embedder


def test_search_ranks_by_cosine_similarity() -> None:
    chunks = [chunk("a", "texte a", "A"), chunk("b", "texte b", "B"), chunk("c", "texte c", "C")]
    retriever, _, _ = build(
        chunks,
        {"texte a": [1.0, 0.0], "texte b": [0.0, 1.0], "texte c": [0.7, 0.7], "une requête": [1.0, 0.0]},
    )

    hits = retriever.search("une requête", "fr", top_k=2)

    assert [hit.chunk.id for hit in hits] == ["a", "c"]
    assert hits[0].score > 0.99  # identical vector -> similarity ~1.0
    assert hits[0].chunk.source_label == "A"
    assert hits[0].chunk.category == "profile"


def test_document_is_ingested_once_per_language() -> None:
    chunks = [chunk("a", "texte a", "A")]
    retriever, knowledge, embedder = build(chunks, {"texte a": [1.0, 0.0], "q": [1.0, 0.0]})

    retriever.search("q", "fr", top_k=1)
    retriever.search("q", "fr", top_k=1)

    assert knowledge.calls == 1  # the index is kept after the first touch
    # One batch for the document, then one per query.
    assert embedder.batches == [1, 1, 1]


def test_index_and_prune_only_touch_their_own_source() -> None:
    doc = [chunk("doc-1", "texte a", "Doc")]
    retriever, _, _ = build(
        doc,
        {
            "texte a": [1.0, 0.0],
            "projet 1": [0.9, 0.1],
            "projet 2": [0.8, 0.2],
            "q": [1.0, 0.0],
        },
    )

    retriever.index("fr", [chunk("p1", "projet 1", "P1", "projects"), chunk("p2", "projet 2", "P2", "projects")], "admin_project")
    assert {hit.chunk.id for hit in retriever.search("q", "fr", top_k=5)} == {"doc-1", "p1", "p2"}

    # Dropping p2 from the catalog prunes only it — the document stays.
    retriever.prune("fr", "admin_project", keep_ids=["p1"])
    assert {hit.chunk.id for hit in retriever.search("q", "fr", top_k=5)} == {"doc-1", "p1"}


def test_index_replaces_a_chunk_with_the_same_id() -> None:
    retriever, _, _ = build([], {"v1": [1.0, 0.0], "v2": [0.0, 1.0], "q": [0.0, 1.0]})
    retriever.index("fr", [chunk("p1", "v1", "Ancien", "projects")], "admin_project")
    retriever.index("fr", [chunk("p1", "v2", "Nouveau", "projects")], "admin_project")

    hits = retriever.search("q", "fr", top_k=5)
    assert [(hit.chunk.id, hit.chunk.source_label) for hit in hits] == [("p1", "Nouveau")]
