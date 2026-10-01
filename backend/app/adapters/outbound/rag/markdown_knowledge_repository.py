"""Reads the hand-written knowledge documents (content/afdal.{lang}.md — a
prose CV/bio) and splits them into one chunk per level-2 (`##`) section.

This is the document-chunking step of the RAG pipeline. Projects shown on
the page are deliberately absent from these documents: they come from the
admin-managed catalog instead (see app/domain/project_chunking.py), so the
two never produce competing near-duplicate chunks. The documents only hold
projects that have no card on the page (coursework, personal experiments)."""

import re
from pathlib import Path

from app.domain.models import Category, Chunk, Lang

DEFAULT_CONTENT_DIR = Path(__file__).resolve().parents[4] / "content"

DOCUMENT_SOURCE = "document"

# Maps the part of a heading before a colon (or the whole heading, for
# headings without one) to a category.
_HEADING_TO_CATEGORY: dict[str, Category] = {
    "Profil": "profile",
    "Profile": "profile",
    "Formation": "profile",
    "Education": "profile",
    "Ce site": "profile",
    "This site": "profile",
    "Disponibilité": "avail",
    "Availability": "avail",
    "Collaboration non-technique": "team",
    "Non-technical collaboration": "team",
    "Expérience": "experience",
    "Experience": "experience",
    "Projet": "projects",
    "Project": "projects",
    "Projet académique": "projects",
    "Academic project": "projects",
    "Projet personnel": "projects",
    "Personal project": "projects",
    "Compétences": "skills",
    "Skills": "skills",
    "Contact": "contact",
}


def _slugify(heading: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")


def resolve_category(heading: str) -> Category:
    prefix = heading.split(":")[0].strip()
    if prefix not in _HEADING_TO_CATEGORY:
        raise ValueError(f"Unknown heading category for {heading!r}")
    return _HEADING_TO_CATEGORY[prefix]


class MarkdownKnowledgeRepository:
    def __init__(self, content_dir: Path = DEFAULT_CONTENT_DIR) -> None:
        self._content_dir = content_dir

    def chunks(self, lang: Lang) -> list[Chunk]:
        text = (self._content_dir / f"afdal.{lang}.md").read_text(encoding="utf-8")

        # Split on level-2 headings; part [0] is the H1 title, discarded.
        sections = re.split(r"\n## ", text)[1:]

        chunks: list[Chunk] = []
        for section in sections:
            heading, _, body = section.partition("\n")
            heading = heading.strip()
            chunks.append(
                Chunk(
                    id=f"{lang}-{_slugify(heading)}",
                    lang=lang,
                    category=resolve_category(heading),
                    text=f"{heading}\n{body.strip()}",
                    source_label=heading,
                )
            )
        return chunks
