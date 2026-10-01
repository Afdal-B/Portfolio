"""Minimal client for the Upstash Redis REST API, shared by every adapter
that keeps state in Upstash (statistics, project catalog, images, cached
embeddings). One HTTPS call per operation suits serverless functions, which
can't keep a connection pool alive."""

from typing import Any, Optional

import httpx


class UpstashClient:
    def __init__(self, url: str, token: str, http: Optional[httpx.Client] = None) -> None:
        self._url = url.rstrip("/")
        self._token = token
        self._http = http or httpx.Client(timeout=5.0)

    def pipeline(self, commands: list[list[Any]]) -> list[Any]:
        """Runs several commands in one request; returns their results in order."""
        response = self._http.post(
            f"{self._url}/pipeline",
            headers={"Authorization": f"Bearer {self._token}"},
            json=[[str(part) for part in command] for command in commands],
        )
        response.raise_for_status()
        results = []
        for item in response.json():
            if "error" in item:
                raise RuntimeError(f"Upstash error: {item['error']}")
            results.append(item.get("result"))
        return results

    def get(self, key: str) -> Optional[str]:
        return self.pipeline([["GET", key]])[0]

    def set(self, key: str, value: str) -> None:
        self.pipeline([["SET", key, value]])

    def hmget(self, key: str, fields: list[str]) -> list[Optional[str]]:
        if not fields:
            return []
        return self.pipeline([["HMGET", key, *fields]])[0]

    def hset(self, key: str, mapping: dict[str, str]) -> None:
        if not mapping:
            return
        flat: list[Any] = ["HSET", key]
        for field, value in mapping.items():
            flat += [field, value]
        self.pipeline([flat])
