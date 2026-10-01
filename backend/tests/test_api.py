"""HTTP contract tests — the wire format the frontend depends on."""

from fastapi.testclient import TestClient

from app.adapters.inbound.http.dependencies import get_project_service
from app.adapters.outbound.persistence.json_project_repository import JsonProjectRepository
from app.domain.models import Project
from app.domain.services.project_service import ProjectService
from app.main import app

client = TestClient(app)


def test_health() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_chat_projects() -> None:
    res = client.post("/api/chat", json={"message": "voir les projets", "lang": "fr"})
    assert res.status_code == 200
    body = res.json()
    assert body["intent"] == "projects"
    assert body["confidence"] == 92
    assert body["sources"] == ["Projets : fiches détaillées", "Résultats et métriques"]


def test_chat_priority_collision_projects_over_skills() -> None:
    res = client.post(
        "/api/chat",
        json={"message": "quel est le stack et les compétences du projet", "lang": "fr"},
    )
    assert res.json()["intent"] == "projects"


def test_chat_nocv_english() -> None:
    res = client.post("/api/chat", json={"message": "cv téléchargeable", "lang": "en"})
    body = res.json()
    assert body["intent"] == "nocv"
    assert body["confidence"] is None


def test_chat_fallback() -> None:
    res = client.post("/api/chat", json={"message": "asdkjasd", "lang": "fr"})
    body = res.json()
    assert body["intent"] == "fallback"
    assert body["confidence"] is None


def test_chat_rejects_empty_and_oversized_messages() -> None:
    assert client.post("/api/chat", json={"message": "", "lang": "fr"}).status_code == 422
    assert client.post("/api/chat", json={"message": "x" * 501, "lang": "fr"}).status_code == 422


def test_chat_response_contract_shape() -> None:
    res = client.post("/api/chat", json={"message": "qui est Afdal ?", "lang": "fr"})
    body = res.json()
    assert isinstance(body["answer"], str) and body["answer"]
    assert body["sources"] is None or isinstance(body["sources"], list)
    assert body["confidence"] is None or (0 <= body["confidence"] <= 100)
    assert "kind" not in body
    assert body["engine"] in {"scripted", "rag"}


def test_content_projects(tmp_path) -> None:
    # The real catalog is edited through the admin, so this test pins its own
    # data instead of asserting on whatever projects.json holds today.
    repository = JsonProjectRepository(tmp_path / "projects.json")
    repository.replace_all(
        [
            Project(
                id="p",
                meta={"fr": "NLP", "en": "NLP"},
                title={"fr": "Titre", "en": "Title"},
                result={"fr": "r", "en": "r"},
                problem={"fr": "p", "en": "p"},
                method={"fr": "m", "en": "m"},
                stack="Python · PyTorch · MLflow",
                metrics={"fr": "x", "en": "x"},
                url="https://example.org/demo",
            )
        ]
    )
    service = ProjectService(repository=repository, image_store=None)  # type: ignore[arg-type]
    app.dependency_overrides[get_project_service] = lambda: service
    try:
        res = client.get("/api/content/projects", params={"lang": "en"})
    finally:
        app.dependency_overrides.clear()

    assert res.status_code == 200
    [project] = res.json()
    assert project["title"] == "Title"  # localized
    assert project["stack"] == "Python · PyTorch · MLflow"
    assert project["url"] == "https://example.org/demo"


def test_real_catalog_is_well_formed() -> None:
    """Guards the content actually shipped: every project must be complete
    in both languages, whatever the admin changed."""
    projects = JsonProjectRepository().list_all()
    assert projects
    assert len({p.id for p in projects}) == len(projects)
    for project in projects:
        # Metrics are optional: not every project has numbers to show, and the
        # detail view hides the block when it's empty.
        for field in ("meta", "title", "result", "problem", "method"):
            for lang in ("fr", "en"):
                assert getattr(project, field)[lang].strip(), f"{project.id}.{field}.{lang} is empty"


def test_content_experience() -> None:
    res = client.get("/api/content/experience", params={"lang": "fr"})
    assert res.status_code == 200
    experience = res.json()
    assert len(experience) == 3
    first = experience[0]
    assert first["company"] == "ContentSide"
    assert len(first["bullets"]) == 5
    assert first["context"].strip()
    stack = {s["name"]: s for s in first["stack"]}
    assert stack["Quarkus"]["icon"] == "quarkus"


def test_experience_stack_items_have_an_icon_or_glyph() -> None:
    for exp in client.get("/api/content/experience", params={"lang": "en"}).json():
        for item in exp["stack"]:
            assert item["icon"] or item["glyph"], f"{exp['company']}: {item['name']} has no icon"


def test_content_skills_java_uses_its_own_logo() -> None:
    res = client.get("/api/content/skills", params={"lang": "fr"})
    lang_group = next(g for g in res.json() if g["id"] == "lang")
    java = next(s for s in lang_group["skills"] if s["name"] == "Java")
    assert java["icon"] == "java"


def test_content_skills_resolve_glyph_paths() -> None:
    res = client.get("/api/content/skills", params={"lang": "fr"})
    lang_group = next(g for g in res.json() if g["id"] == "lang")
    sql = next(s for s in lang_group["skills"] if s["name"] == "SQL")
    assert sql["icon"] is None
    assert sql["glyph"] and sql["glyph"][0].startswith("M3 5c0")


def test_content_contacts() -> None:
    contacts = client.get("/api/content/contacts").json()
    assert {c["key"] for c in contacts} == {"Email", "LinkedIn", "GitHub", "Hugging Face"}
    # No placeholder link may ship: every contact must actually lead somewhere.
    assert all(c["href"] not in ("", "#") for c in contacts)


def test_content_suggestions_excludes_hidden() -> None:
    ids = {s["id"] for s in client.get("/api/content/suggestions", params={"lang": "fr"}).json()}
    assert "nocv" not in ids
    assert {"profile", "experience", "avail", "projects", "skills", "contact", "team"} <= ids


def test_project_stack_items_carry_catalog_icons() -> None:
    projects = client.get("/api/content/projects", params={"lang": "fr"}).json()
    items = {item["name"]: item for p in projects for item in p["stack_items"]}
    # A trailing precision doesn't prevent the match, and the name is kept as written.
    assert items["PySpark (ALS)"]["icon"] == "apachespark"
    assert items["Streamlit"]["icon"] == "streamlit"


def test_unknown_stack_item_has_no_icon() -> None:
    from app.adapters.outbound.persistence.static_content_repository import StaticSkillRepository

    skill = StaticSkillRepository().resolve("Une techno inconnue")
    assert skill.name == "Une techno inconnue"
    assert skill.icon is None and skill.glyph is None
