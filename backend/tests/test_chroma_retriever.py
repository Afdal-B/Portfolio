"""Chroma adapter, driven with an in-memory client and a fake embedder — no
disk writes, no model download."""

import uuid

import chromadb

from app.adapters.outbound.rag.chroma_retriever import ChromaRetriever
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
    retriever = ChromaRetriever(
        knowledge=knowledge,
        embedder=embedder,
        client=chromadb.EphemeralClient(),
        # Ephemeral clients share one in-process store, so each test needs
        # its own collection namespace.
        collection_prefix=f"test_{uuid.uuid4().hex}",
    )
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

    assert knowledge.calls == 1  # collection is cached after the first touch
    # One batch for the document, then one per query.
    assert embedder.batches == [1, 1, 1]


def test_section_removed_from_document_is_purged_on_ingestion() -> None:
    """upsert never deletes — a section dropped from the markdown used to
    stay retrievable forever."""
    client = chromadb.EphemeralClient()
    prefix = f"test_{uuid.uuid4().hex}"
    vectors = {"texte a": [1.0, 0.0], "texte b": [0.0, 1.0], "q": [1.0, 0.0]}

    before = ChromaRetriever(
        knowledge=FakeKnowledge([chunk("a", "texte a", "A"), chunk("b", "texte b", "B")]),
        embedder=FakeEmbedder(vectors),
        client=client,
        collection_prefix=prefix,
    )
    before.search("q", "fr", top_k=5)

    # Next startup: section "b" has been removed from the document.
    after = ChromaRetriever(
        knowledge=FakeKnowledge([chunk("a", "texte a", "A")]),
        embedder=FakeEmbedder(vectors),
        client=client,
        collection_prefix=prefix,
    )
    assert {hit.chunk.id for hit in after.search("q", "fr", top_k=5)} == {"a"}


def test_legacy_untagged_chunks_are_purged_but_other_sources_kept() -> None:
    client = chromadb.EphemeralClient()
    prefix = f"test_{uuid.uuid4().hex}"
    collection = client.get_or_create_collection(f"{prefix}_fr", metadata={"hnsw:space": "cosine"})
    # A chunk ingested before the `source` tag existed, and a project chunk.
    collection.upsert(
        ids=["old-projet", "fr-admin-project-x"],
        embeddings=[[0.9, 0.1], [0.8, 0.2]],
        documents=["ancien projet", "projet x"],
        metadatas=[
            {"category": "projects", "source_label": "Ancien"},
            {"category": "projects", "source_label": "X", "source": "admin_project"},
        ],
    )

    retriever = ChromaRetriever(
        knowledge=FakeKnowledge([chunk("a", "texte a", "A")]),
        embedder=FakeEmbedder({"texte a": [1.0, 0.0], "q": [1.0, 0.0]}),
        client=client,
        collection_prefix=prefix,
    )

    ids = {hit.chunk.id for hit in retriever.search("q", "fr", top_k=5)}
    assert ids == {"a", "fr-admin-project-x"}


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
