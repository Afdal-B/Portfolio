"""Visitor-facing content must not contain em dashes: on a portfolio they
read as machine-written. Code comments are free to use them; this only
scans what ends up on screen or in the assistant's answers."""

from pathlib import Path

import pytest

from app.adapters.outbound.llm.gemini_answer_generator import _strip_em_dashes

BACKEND = Path(__file__).resolve().parents[1]
STATIC_DATA = BACKEND / "app" / "adapters" / "outbound" / "persistence" / "static_data"

VISIBLE_FILES = [
    BACKEND / "content" / "afdal.fr.md",
    BACKEND / "content" / "afdal.en.md",
    BACKEND / "storage" / "projects.json",
]


@pytest.mark.parametrize("path", VISIBLE_FILES, ids=lambda p: p.name)
def test_no_em_dash_in_visible_files(path: Path) -> None:
    assert "—" not in path.read_text(encoding="utf-8")


def _string_literals(path: Path) -> list[str]:
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings
    ]


@pytest.mark.parametrize("name", ["qa.py", "copy.py", "experience.py", "skills.py"])
def test_no_em_dash_in_static_content(name: str) -> None:
    offenders = [s for s in _string_literals(STATIC_DATA / name) if "—" in s]
    assert not offenders


def test_generated_answers_lose_their_em_dashes() -> None:
    assert _strip_em_dashes("Il est disponible — immédiatement.") == "Il est disponible, immédiatement."
