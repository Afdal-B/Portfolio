"""Project use cases, with fake ports."""

from app.domain.models import Project
from app.domain.services.project_service import ProjectService


def project(id_: str, title: str) -> Project:
    return Project(
        id=id_,
        meta={"fr": "NLP", "en": "NLP"},
        title={"fr": title, "en": title},
        result={"fr": "r", "en": "r"},
        problem={"fr": "p", "en": "p"},
        method={"fr": "m", "en": "m"},
        stack="Python",
        metrics={"fr": "x", "en": "x"},
    )


class InMemoryRepository:
    def __init__(self, projects):
        self._projects = list(projects)

    def list_all(self):
        return list(self._projects)

    def replace_all(self, projects):
        self._projects = list(projects)
        return list(projects)


class RecordingRetriever:
    def __init__(self):
        self.indexed = []
        self.pruned = []

    def search(self, query, lang, top_k):
        return []

    def index(self, lang, chunks, source):
        self.indexed.append((lang, [c.id for c in chunks], source))

    def prune(self, lang, source, keep_ids):
        self.pruned.append((lang, source, list(keep_ids)))


class NoImages:
    def save(self, content):
        raise AssertionError("not expected")


class ExplodingRetriever(RecordingRetriever):
    def index(self, lang, chunks, source):
        raise RuntimeError("vector store down")


def test_sync_index_indexes_the_catalog_already_on_disk() -> None:
    """Regression: projects were only indexed on an admin save, so a fresh
    vector store knew nothing about them."""
    retriever = RecordingRetriever()
    service = ProjectService(InMemoryRepository([project("a", "A")]), NoImages(), retriever)

    service.sync_index()

    # Each project, plus the overview chunk that names them all.
    assert retriever.indexed == [
        ("fr", ["fr-admin-project-a", "fr-admin-projects-overview"], "admin_project"),
        ("en", ["en-admin-project-a", "en-admin-projects-overview"], "admin_project"),
    ]


def test_sync_index_without_a_retriever_is_a_no_op() -> None:
    ProjectService(InMemoryRepository([project("a", "A")]), NoImages(), retriever=None).sync_index()


def test_replace_all_survives_a_retrieval_failure() -> None:
    """The catalog is persisted first; a vector-store hiccup must not turn a
    successful save into an error."""
    repository = InMemoryRepository([])

    stored = ProjectService(repository, NoImages(), ExplodingRetriever()).replace_all([project("a", "A")])

    assert [p.id for p in stored] == ["a"]
    assert [p.id for p in repository.list_all()] == ["a"]


def test_overview_chunk_names_every_project() -> None:
    from app.domain.project_chunking import overview_chunk

    chunk = overview_chunk([project("a", "Alpha"), project("b", "Beta")], "fr")
    assert "Alpha" in chunk.text and "Beta" in chunk.text
    assert chunk.category == "projects"
