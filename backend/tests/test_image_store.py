"""Image upload: the store itself, plus the HTTP endpoint around it."""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.adapters.inbound.http.dependencies import get_project_service
from app.adapters.outbound.persistence.filesystem_image_store import FilesystemImageStore
from app.domain.errors import ImageRejected
from app.domain.services.project_service import ProjectService
from app.main import app

client = TestClient(app)

PASSWORD = "test-admin-password"


def make_image(width: int = 40, height: int = 30, fmt: str = "PNG") -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), "teal").save(buffer, format=fmt)
    return buffer.getvalue()


class NullProjectRepository:
    def list_all(self):
        return []

    def replace_all(self, projects):
        return list(projects)


@pytest.fixture
def store(tmp_path):
    return FilesystemImageStore(upload_dir=tmp_path)


@pytest.fixture
def upload_api(tmp_path, offline_container, store):
    offline_container.settings.admin_password = PASSWORD
    service = ProjectService(repository=NullProjectRepository(), image_store=store)
    app.dependency_overrides[get_project_service] = lambda: service
    yield tmp_path
    app.dependency_overrides.clear()


def auth() -> dict[str, str]:
    return {"Authorization": f"Bearer {PASSWORD}"}


def post(content: bytes, filename: str = "photo.png", content_type: str = "image/png"):
    return client.post("/api/admin/uploads", files={"file": (filename, content, content_type)}, headers=auth())


# --- the store itself ---------------------------------------------------


def test_stores_webp_and_ignores_client_filename(store, tmp_path) -> None:
    url = store.save(make_image())

    assert url.startswith("/api/uploads/") and url.endswith(".webp")
    stored = list(tmp_path.iterdir())
    assert len(stored) == 1
    assert stored[0].name != "photo.png"
    with Image.open(stored[0]) as saved:
        assert saved.format == "WEBP"


def test_large_image_is_downscaled(store, tmp_path) -> None:
    store.save(make_image(3000, 2000))

    with Image.open(next(iter(tmp_path.iterdir()))) as saved:
        assert saved.size == (1600, 1067)  # capped, aspect ratio preserved


def test_small_image_is_not_upscaled(store, tmp_path) -> None:
    store.save(make_image(40, 30))

    with Image.open(next(iter(tmp_path.iterdir()))) as saved:
        assert saved.size == (40, 30)


def test_jpeg_is_converted(store, tmp_path) -> None:
    store.save(make_image(fmt="JPEG"))

    with Image.open(next(iter(tmp_path.iterdir()))) as saved:
        assert saved.format == "WEBP"


def test_non_image_bytes_are_rejected(store, tmp_path) -> None:
    with pytest.raises(ImageRejected):
        store.save(b"<svg/>")
    assert list(tmp_path.iterdir()) == []


def test_oversized_file_is_rejected(tmp_path) -> None:
    small_cap_store = FilesystemImageStore(upload_dir=tmp_path, max_bytes=32)

    with pytest.raises(ImageRejected):
        small_cap_store.save(make_image(200, 200))
    assert list(tmp_path.iterdir()) == []


# --- through the API ----------------------------------------------------


def test_upload_requires_admin(upload_api) -> None:
    res = client.post("/api/admin/uploads", files={"file": ("a.png", make_image(), "image/png")})
    assert res.status_code == 401


def test_upload_returns_url(upload_api) -> None:
    res = post(make_image())

    assert res.status_code == 200
    assert res.json()["url"].endswith(".webp")


def test_upload_rejects_non_image_despite_image_content_type(upload_api) -> None:
    # The declared Content-Type is not trusted — decoding is what decides.
    res = post(b"<svg/>", filename="payload.svg", content_type="image/png")

    assert res.status_code == 400
    assert list(upload_api.iterdir()) == []
