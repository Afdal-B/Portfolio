"""Rebuilds content/embeddings.json: the precomputed vectors of every passage
the assistant indexes (knowledge documents and project catalog, FR and EN).

Run after editing content/afdal.*.md or storage/projects.json, then commit
the file:  make embeddings

Calls the Gemini embedding API once per passage (about 40 per language),
batched, using PORTFOLIO_GEMINI_API_KEY from backend/.env. Passages already
in the cache are reused, and entries no longer used are dropped."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.adapters.outbound.rag.embedder import GeminiEmbedder  # noqa: E402
from app.adapters.outbound.rag.embedding_cache import (  # noqa: E402
    DEFAULT_CACHE_PATH,
    cache_key,
    read_cache,
    write_cache,
)
from app.container import container  # noqa: E402

TASK = "RETRIEVAL_DOCUMENT"


def main() -> None:
    settings = container.settings
    if not settings.gemini_api_key:
        sys.exit("PORTFOLIO_GEMINI_API_KEY is not set (backend/.env).")
    model, dimensions = settings.embedding_model, settings.embedding_dimensions

    texts = sorted({chunk.text for chunk in container.indexed_chunks()})
    previous = read_cache(DEFAULT_CACHE_PATH, model, dimensions)
    vectors = {}
    missing = []
    for text in texts:
        key = cache_key(model, dimensions, TASK, text)
        if key in previous:
            vectors[key] = previous[key]
        else:
            missing.append(text)

    if missing:
        embedder = GeminiEmbedder(settings.gemini_api_key, model, dimensions)
        for text, vector in zip(missing, embedder.embed_documents(missing)):
            vectors[cache_key(model, dimensions, TASK, text)] = vector

    write_cache(DEFAULT_CACHE_PATH, model, dimensions, vectors)
    print(f"{len(texts)} passages, {len(missing)} embedded now, written to {DEFAULT_CACHE_PATH}")


if __name__ == "__main__":
    main()
