"""Per-visitor rate limit on the chat endpoint.

Each question may cost a call to a quota-limited LLM (a few hundred free
requests a day), so one visitor looping on the chat must not drain it for
everyone. In-memory and per process: enough for a single-instance
portfolio, and it resets on restart, which is acceptable here."""

import threading
import time
from collections import deque
from typing import Callable, Optional

from fastapi import HTTPException, Request, status


class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, now: Optional[float] = None) -> bool:
        now = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and now - hits[0] >= self._window:
                hits.popleft()
            if len(hits) >= self._max:
                return False
            hits.append(now)
            # Keep memory bounded: drop visitors with no recent activity.
            if len(self._hits) > 10_000:
                self._hits = {k: v for k, v in self._hits.items() if v and now - v[-1] < self._window}
            return True


def client_key(request: Request) -> str:
    """The visitor's address. Behind a proxy (Vercel rewrite, container
    ingress) the socket peer is the proxy, so the first X-Forwarded-For
    entry, set by the edge, identifies the visitor."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def enforce(
    limiter: SlidingWindowLimiter, request: Request, on_reject: Optional[Callable[[], None]] = None
) -> None:
    if not limiter.allow(client_key(request)):
        if on_reject is not None:
            on_reject()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many questions, try again later.",
        )
