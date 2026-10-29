"""make pull-projects, driven with a fake site: no network."""

import importlib.util
import json
from pathlib import Path

import httpx

from app.adapters.outbound.persistence.json_project_repository import JsonProjectRepository

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pull_projects.py"
spec = importlib.util.spec_from_file_location("pull_projects", SCRIPT)
pull_projects = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pull_projects)

IMAGE = "a" * 32 + ".webp"


def online_project(id_: str, image: str = "") -> dict:
    text = {"fr": f"Projet {id_}", "en": f"Project {id_}"}
    return {
        "id": id_, "meta": text, "title": text, "result": text, "problem": text, "method": text,
        "stack": "Python", "metrics": text, "url": "#", "image_url": image, "screenshots": [],
        "image_seed": "", "summary": text, "code_url": "",
    }


def fake_site(catalog: list[dict], password: str = "pw") -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/admin/projects":
            if request.headers.get("authorization") != f"Bearer {password}":
                return httpx.Response(401)
            return httpx.Response(200, json=catalog)
        if request.url.path == f"/api/uploads/{IMAGE}":
            return httpx.Response(200, content=b"webp-bytes")
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_online_catalog_and_missing_images_are_copied_locally(tmp_path: Path) -> None:
    repository = JsonProjectRepository(tmp_path / "projects.json")
    repository.replace_all([JsonProjectRepository().list_all()[0]])  # a stale local catalog
    catalog = [online_project("created-online", image=f"/api/uploads/{IMAGE}")]

    result = pull_projects.pull(fake_site(catalog), "https://site", "pw", repository, tmp_path / "uploads")

    assert [p.id for p in repository.list_all()] == ["created-online"]
    assert result["added"] == ["created-online"] and result["removed"]
    assert (tmp_path / "uploads" / IMAGE).read_bytes() == b"webp-bytes"
    assert json.loads((tmp_path / "projects.json").read_text())[0]["title"]["en"] == "Project created-online"


def test_a_wrong_password_stops_without_touching_the_catalog(tmp_path: Path) -> None:
    repository = JsonProjectRepository(tmp_path / "projects.json")
    repository.replace_all([JsonProjectRepository().list_all()[0]])
    before = (tmp_path / "projects.json").read_text()
    try:
        pull_projects.pull(fake_site([], password="pw"), "https://site", "faux", repository, tmp_path / "uploads")
    except SystemExit as exit_:
        assert "PORTFOLIO_PROD_ADMIN_PASSWORD" in str(exit_)
    assert (tmp_path / "projects.json").read_text() == before
