"""Embeddings computed by the Gemini API.

Remote rather than a local model so the backend stays small enough for
serverless hosting (no PyTorch). The client is created lazily: importing
this module never touches the network, which keeps the scripted (no-LLM)
path and the test suite offline."""

import math
from typing import Any, Optional

# The API accepts at most this many texts per embed_content call.
_BATCH_SIZE = 100


class GeminiEmbedder:
    def __init__(self, api_key: str, model: str, dimensions: int, client: Optional[Any] = None) -> None:
        self._api_key = api_key
        self._model = model
        self._dimensions = dimensions
        self._client = client

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), _BATCH_SIZE):
            vectors.extend(self._embed(texts[start : start + _BATCH_SIZE], "RETRIEVAL_DOCUMENT"))
        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], "RETRIEVAL_QUERY")[0]

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        from google.genai import types

        result = self._get_client().models.embed_content(
            model=self._model,
            contents=texts,
            config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=self._dimensions),
        )
        # Below the model's full size, vectors come back unnormalized.
        return [_normalize(list(embedding.values)) for embedding in result.embeddings]

    def _get_client(self) -> Any:
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector
