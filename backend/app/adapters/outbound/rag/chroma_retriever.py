"""Retriever backed by ChromaDB: a local vector store persisted on disk
(backend/.chroma/ by default, /tmp on serverless hosts), so embeddings
survive restarts where the disk does. One collection per language, cosine
space.

On first use per language it ingests the knowledge document; project chunks
are pushed in separately by ProjectService whenever the catalog is saved.
Chunks carry a `source` tag so one source can be pruned without touching the
other."""

from pathlib import Path
from typing import Any, Optional, Sequence

from app.domain.models import Chunk, Lang, RetrievedChunk
from app.domain.ports import Embedder, KnowledgeRepository

DEFAULT_CHROMA_PATH = Path(__file__).resolve().parents[4] / ".chroma"


class ChromaRetriever:
    def __init__(
        self,
        knowledge: KnowledgeRepository,
        embedder: Embedder,
        chroma_path: Path = DEFAULT_CHROMA_PATH,
        client: Optional[Any] = None,
        document_source: str = "document",
        collection_prefix: str = "afdal_knowledge",
    ) -> None:
        self._knowledge = knowledge
        self._embedder = embedder
        self._chroma_path = chroma_path
        self._client = client
        self._document_source = document_source
        self._collection_prefix = collection_prefix
        self._collections: dict[str, Any] = {}

    # --- Retriever port -------------------------------------------------

    def search(self, query: str, lang: Lang, top_k: int) -> list[RetrievedChunk]:
        collection = self._collection(lang)
        vector = self._embedder.embed_query(query)
        result = collection.query(query_embeddings=[vector], n_results=top_k)

        hits: list[RetrievedChunk] = []
        for id_, text, meta, distance in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            chunk = Chunk(
                id=id_,
                lang=lang,
                category=meta["category"],
                text=text,
                source_label=meta["source_label"],
            )
            # Cosine space: distance = 1 - cosine similarity.
            hits.append(RetrievedChunk(chunk=chunk, score=1 - distance))
        return hits

    def index(self, lang: Lang, chunks: Sequence[Chunk], source: str) -> None:
        if not chunks:
            return
        collection = self._collection(lang)
        self._upsert(collection, chunks, source)

    def prune(self, lang: Lang, source: str, keep_ids: Sequence[str]) -> None:
        collection = self._collection(lang)
        existing = collection.get(where={"source": source})
        stale = [id_ for id_ in existing["ids"] if id_ not in set(keep_ids)]
        if stale:
            collection.delete(ids=stale)

    # --- internals ------------------------------------------------------

    def _collection(self, lang: Lang) -> Any:
        if lang not in self._collections:
            collection = self._get_client().get_or_create_collection(
                f"{self._collection_prefix}_{lang}", metadata={"hnsw:space": "cosine"}
            )
            chunks = self._knowledge.chunks(lang)
            # upsert alone never deletes: a section removed from the document
            # would otherwise stay retrievable forever.
            self._drop_orphaned_document_chunks(collection, {chunk.id for chunk in chunks})
            if chunks:
                self._upsert(collection, chunks, self._document_source)
            self._collections[lang] = collection
        return self._collections[lang]

    def _drop_orphaned_document_chunks(self, collection: Any, current_ids: set[str]) -> None:
        """Removes document chunks that are no longer in the document.

        Chunks with no `source` tag predate tagging and can only have come
        from the document, so they're treated as document chunks too. Chunks
        from any other source (e.g. the project catalog) are left alone."""
        existing = collection.get(include=["metadatas"])
        orphaned = [
            id_
            for id_, meta in zip(existing["ids"], existing["metadatas"])
            if (meta or {}).get("source", self._document_source) == self._document_source
            and id_ not in current_ids
        ]
        if orphaned:
            collection.delete(ids=orphaned)

    def _get_client(self) -> Any:
        if self._client is None:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self._client = chromadb.PersistentClient(
                path=str(self._chroma_path), settings=ChromaSettings(anonymized_telemetry=False)
            )
        return self._client

    def _upsert(self, collection: Any, chunks: Sequence[Chunk], source: str) -> None:
        texts = [chunk.text for chunk in chunks]
        collection.upsert(
            ids=[chunk.id for chunk in chunks],
            embeddings=self._embedder.embed_documents(texts),
            documents=texts,
            metadatas=[
                {"category": chunk.category, "source_label": chunk.source_label, "source": source}
                for chunk in chunks
            ],
        )

    def warm_up(self, langs: Sequence[Lang]) -> None:
        """Eagerly ingests documents at startup so the first visitor doesn't
        pay for it."""
        for lang in langs:
            self._collection(lang)
