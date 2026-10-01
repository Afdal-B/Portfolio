"""Precomputed document embeddings, shipped with the code.

On serverless hosting every new instance rebuilds its vector index. Without
this cache, each one would embed the whole corpus again through the Gemini
API, whose free tier allows only 100 embeddings per minute: a handful of
cold starts is enough to exhaust it. With it, an instance indexes the corpus
without a single API call; only visitors' questions are embedded live.

The file is produced by `make embeddings` (scripts/build_embeddings.py) and
committed. Entries are keyed by model, size, task and text, so a passage
whose wording changed simply misses the cache and is embedded live, never
matched to a stale vector."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

from app.domain.ports import Embedder

logger = logging.getLogger(__name__)

DEFAULT_CACHE_PATH = Path(__file__).resolve().parents[4] / "content" / "embeddings.json"

_DOCUMENT_TASK = "RETRIEVAL_DOCUMENT"


def cache_key(model: str, dimensions: int, task: str, text: str) -> str:
    return hashlib.sha256(f"{model}\n{dimensions}\n{task}\n{text}".encode("utf-8")).hexdigest()


class CachedEmbedder:
    """Wraps an Embedder: document vectors come from the file when present.
    Queries always go to the wrapped embedder, since they're never known in
    advance."""

    def __init__(
        self,
        inner: Embedder,
        model: str,
        dimensions: int,
        path: Path = DEFAULT_CACHE_PATH,
    ) -> None:
        self._inner = inner
        self._model = model
        self._dimensions = dimensions
        self._path = path
        self._vectors: Optional[dict[str, list[float]]] = None

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._load()
        keys = [cache_key(self._model, self._dimensions, _DOCUMENT_TASK, text) for text in texts]
        missing = [text for text, key in zip(texts, keys) if key not in vectors]
        if missing:
            logger.warning("%d passage(s) missing from the embedding cache; run `make embeddings`", len(missing))
            for key, vector in zip(
                [cache_key(self._model, self._dimensions, _DOCUMENT_TASK, t) for t in missing],
                self._inner.embed_documents(missing),
            ):
                vectors[key] = vector
        return [vectors[key] for key in keys]

    def embed_query(self, text: str) -> list[float]:
        return self._inner.embed_query(text)

    def _load(self) -> dict[str, list[float]]:
        if self._vectors is None:
            self._vectors = read_cache(self._path, self._model, self._dimensions)
        return self._vectors


def read_cache(path: Path, model: str, dimensions: int) -> dict[str, list[float]]:
    """The cached vectors, or nothing when the file is absent or was built
    with another model or size (its vectors wouldn't be comparable)."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("model") != model or data.get("dimensions") != dimensions:
        return {}
    return dict(data.get("vectors", {}))


def write_cache(path: Path, model: str, dimensions: int, vectors: dict[str, list[float]]) -> None:
    payload = {
        "model": model,
        "dimensions": dimensions,
        # Rounded: plenty for cosine similarity, and a third of the file size.
        "vectors": {key: [round(v, 6) for v in vector] for key, vector in sorted(vectors.items())},
    }
    path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
