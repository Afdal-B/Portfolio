import pytest

from app.config import Settings
from app.container import container

CACHED = (
    "project_repository",
    "image_store",
    "qa_repository",
    "copy_repository",
    "retriever",
    "primary_generator",
    "scripted_generator",
    "chat_service",
    "content_service",
    "project_service",
    "analytics_store",
    "analytics_service",
)


@pytest.fixture(autouse=True)
def offline_container(monkeypatch):
    """Gives every test a pristine, offline container.

    Tests must not depend on whatever is in a developer's local backend/.env
    (a real Gemini key there would otherwise make the suite hit the network),
    and cached_property values must not leak between tests.
    """
    for name in CACHED:
        container.__dict__.pop(name, None)

    monkeypatch.setattr(
        container,
        "settings",
        Settings(gemini_api_key=None, admin_password=None, upstash_redis_rest_url=None, upstash_redis_rest_token=None),
    )

    yield container

    for name in CACHED:
        container.__dict__.pop(name, None)


@pytest.fixture(autouse=True)
def no_chat_rate_limit():
    """The suite asks far more questions than one visitor may; the limit
    itself is covered in test_rate_limit.py."""
    from app.adapters.inbound.http.dependencies import limit_chat_rate
    from app.main import app

    app.dependency_overrides[limit_chat_rate] = lambda: None
    yield
    app.dependency_overrides.pop(limit_chat_rate, None)
