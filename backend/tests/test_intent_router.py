import pytest

from app.domain.intent_router import route


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Voir les projets", "projects"),
        ("What have you delivered recently?", "projects"),
        ("Quelles sont tes compétences ?", "skills"),
        ("What's your tech stack?", "skills"),
        ("Quelle est son expérience professionnelle ?", "experience"),
        ("Did he do an internship?", "experience"),
        ("Le CV est-il téléchargeable ?", "nocv"),
        ("Can I download your resume as a PDF?", "nocv"),
        ("Comment te contacter ?", "contact"),
        ("What's your email or GitHub?", "contact"),
        ("Es-tu en recherche de CDI ?", "avail"),
        ("Are you available for a permanent role?", "avail"),
        ("Travaille-t-il avec des non-tech ?", "team"),
        ("Qui es-tu ?", "profile"),
        ("Tell me about your background", "profile"),
        ("asdkjasdkjasd", "fallback"),
    ],
)
def test_route_matches_expected_intent(text: str, expected: str) -> None:
    assert route(text) == expected


def test_priority_collision_projects_before_skills() -> None:
    # "stack" alone would hit `skills`, but `projet` appears too — `projects`
    # is checked first in the real rule order (ported from onSubmit), so it
    # must win. This is the exact case where the design README's prose intent
    # order diverges from the prototype's actual code.
    assert route("quel est le stack et les compétences du projet") == "projects"


def test_priority_collision_skills_before_nocv() -> None:
    # Text containing both a `skills` keyword ("compét") and a `nocv` keyword
    # ("cv") must resolve to `skills`, since that rule is checked first.
    assert route("je veux voir ton cv et tes compétences") == "skills"


def test_case_insensitive() -> None:
    assert route("VOIR LES PROJETS") == "projects"
