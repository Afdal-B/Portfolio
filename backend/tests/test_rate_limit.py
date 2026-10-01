from fastapi import Request
from fastapi.testclient import TestClient

from app.adapters.inbound.http import rate_limit
from app.adapters.inbound.http.dependencies import limit_chat_rate
from app.main import app


def test_limiter_blocks_past_the_quota_then_recovers() -> None:
    limiter = rate_limit.SlidingWindowLimiter(max_requests=2, window_seconds=60)
    assert limiter.allow("a", now=0)
    assert limiter.allow("a", now=1)
    assert not limiter.allow("a", now=2)
    # Another visitor is unaffected.
    assert limiter.allow("b", now=2)
    # Once the window has passed, the first visitor may ask again.
    assert limiter.allow("a", now=61)


def test_chat_returns_429_once_the_visitor_is_over_the_limit() -> None:
    limiter = rate_limit.SlidingWindowLimiter(max_requests=1, window_seconds=3600)

    def tight_limit(request: Request) -> None:
        rate_limit.enforce(limiter, request)

    app.dependency_overrides[limit_chat_rate] = tight_limit
    client = TestClient(app)
    body = {"message": "voir les projets", "lang": "fr"}
    headers = {"x-forwarded-for": "203.0.113.7"}
    assert client.post("/api/chat", json=body, headers=headers).status_code == 200
    assert client.post("/api/chat", json=body, headers=headers).status_code == 429
    # A different visitor behind the same proxy still gets through.
    assert client.post("/api/chat", json=body, headers={"x-forwarded-for": "198.51.100.2"}).status_code == 200
