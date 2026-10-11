"""Retriever backed by an in-memory vector index: cosine similarity over the
passages' embeddings, one index per language.

The corpus is a few dozen passages, so an exact search over every vector
takes well under a millisecond, and there is nothing to persist: vectors
come precomputed from content/embeddings.json (or the shared cache), and an
instance rebuilds its index in a moment when it starts. This replaced
ChromaDB, whose dependencies (onnxruntime, gRPC, a Kubernetes client...)
weighed several hundred MB and no longer fitted on serverless hosting.

On first use per language it ingests the knowledge document; project chunks
are pushed in separately by ProjectService whenever the catalog changes.
Entries carry a `source` tag so one source can be pruned without touching
the other."""

import math
import threading
from dataclasses import dataclass
from typing import Sequence

from app.domain.models import Chunk, Lang, RetrievedChunk
from app.domain.ports import Embedder, KnowledgeRepository


@dataclass(frozen=True)
class _Entry:
    chunk: Chunk
    source: str
    vector: list[float]


class InMemoryRetriever:
    def __init__(
        self,
        knowledge: KnowledgeRepository,
        embedder: Embedder,
        document_source: str = "document",
    ) -> None:
        self._knowledge = knowledge
        self._embedder = embedder
        self._document_source = document_source
        self._indexes: dict[str, dict[str, _Entry]] = {}
        self._lock = threading.Lock()

    # --- Retriever port -------------------------------------------------

    def search(self, query: str, lang: Lang, top_k: int) -> list[RetrievedChunk]:
        entries = list(self._index(lang).values())
        if not entries:
            return []
        query_vector = self._embedder.embed_query(query)
        scored = [RetrievedChunk(chunk=e.chunk, score=_cosine(query_vector, e.vector)) for e in entries]
        scored.sort(key=lambda hit: hit.score, reverse=True)
        return scored[:top_k]

    def index(self, lang: Lang, chunks: Sequence[Chunk], source: str) -> None:
        if not chunks:
            return
        index = self._index(lang)
        vectors = self._embedder.embed_documents([chunk.text for chunk in chunks])
        with self._lock:
            for chunk, vector in zip(chunks, vectors):
                index[chunk.id] = _Entry(chunk=chunk, source=source, vector=vector)

    def prune(self, lang: Lang, source: str, keep_ids: Sequence[str]) -> None:
        index = self._index(lang)
        keep = set(keep_ids)
        with self._lock:
            for id_ in [id_ for id_, entry in index.items() if entry.source == source and id_ not in keep]:
                del index[id_]

    def warm_up(self, langs: Sequence[Lang]) -> None:
        """Ingests the documents now, so the first question doesn't pay for it."""
        for lang in langs:
            self._index(lang)

    # --- internals ------------------------------------------------------

    def _index(self, lang: Lang) -> dict[str, _Entry]:
        if lang not in self._indexes:
            chunks = self._knowledge.chunks(lang)
            vectors = self._embedder.embed_documents([chunk.text for chunk in chunks]) if chunks else []
            entries = {
                chunk.id: _Entry(chunk=chunk, source=self._document_source, vector=vector)
                for chunk, vector in zip(chunks, vectors)
            }
            with self._lock:
                # Another thread may have built it meanwhile: keep the first.
                self._indexes.setdefault(lang, entries)
        return self._indexes[lang]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0
