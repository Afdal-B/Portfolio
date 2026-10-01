import pytest

from app.adapters.outbound.rag.markdown_knowledge_repository import (
    MarkdownKnowledgeRepository,
    resolve_category,
)

VALID_CATEGORIES = {"profile", "avail", "team", "contact", "projects", "skills", "experience"}

repository = MarkdownKnowledgeRepository()


def test_both_languages_produce_matching_sections() -> None:
    fr = repository.chunks("fr")
    en = repository.chunks("en")
    assert len(fr) == len(en)
    # Same section order/categories in both languages, even though slugs differ.
    assert [c.category for c in fr] == [c.category for c in en]


def test_chunk_ids_are_unique_and_well_formed() -> None:
    ids = [c.id for c in repository.chunks("fr")]
    assert len(ids) == len(set(ids))
    assert all(id_.startswith("fr-") for id_ in ids)


def test_categories_are_valid_and_content_non_empty() -> None:
    for chunk in repository.chunks("fr") + repository.chunks("en"):
        assert chunk.category in VALID_CATEGORIES
        assert chunk.text.strip()
        assert chunk.source_label.strip()
        # The heading itself is included at the top of the chunk text.
        assert chunk.source_label in chunk.text


def test_catalog_projects_are_not_duplicated_in_the_document() -> None:
    # Catalog projects are chunked separately (app/domain/project_chunking.py);
    # repeating one in the document would make near-duplicate chunks compete
    # during retrieval. The document may only hold projects without a card.
    from app.adapters.outbound.persistence.json_project_repository import JsonProjectRepository

    catalog_names = {p.title["fr"].split(":")[0].strip().lower() for p in JsonProjectRepository().list_all()}
    for chunk in repository.chunks("fr"):
        if chunk.category == "projects":
            assert not any(name in chunk.source_label.lower() for name in catalog_names), chunk.source_label


def test_covers_all_three_experiences() -> None:
    assert len([c for c in repository.chunks("fr") if c.category == "experience"]) == 3


def test_unknown_heading_raises() -> None:
    # The resolver rejects a heading with no known prefix, rather than
    # silently mis-categorizing it.
    with pytest.raises(ValueError):
        resolve_category("Un titre inconnu")


def test_heading_category_is_read_before_the_colon() -> None:
    assert resolve_category("Expérience : ContentSide") == "experience"
    assert resolve_category("Experience: ContentSide") == "experience"


def test_education_and_site_sections_are_indexed() -> None:
    labels = [c.source_label for c in repository.chunks("fr")]
    assert "Formation" in labels
    assert "Ce site" in labels
