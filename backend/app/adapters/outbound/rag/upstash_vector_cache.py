"""Embeddings computed online (a project edited in production), shared
across instances through Upstash: each passage is embedded once, not once
per instance start."""

import json
from typing import Optional

from app.adapters.outbound.upstash import UpstashClient

KEY = "pf:embeddings"


class UpstashVectorCache:
    def __init__(self, client: UpstashClient) -> None:
        self._client = client

    def get_many(self, keys: list[str]) -> dict[str, list[float]]:
        values = self._client.hmget(KEY, keys)
        return {key: json.loads(value) for key, value in zip(keys, values) if value}

    def set_many(self, vectors: dict[str, list[float]]) -> None:
        self._client.hset(KEY, {key: json.dumps([round(v, 6) for v in vector]) for key, vector in vectors.items()})
