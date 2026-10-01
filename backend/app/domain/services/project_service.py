"""Project use cases: read the catalog, and replace it while keeping the
retrieval index in step."""

import hashlib
import logging
from typing import Optional, Sequence

from app.domain.models import Project
from app.domain.ports import ImageStore, ProjectRepository, Retriever
from app.domain.project_chunking import (
    LANGS,
    PROJECT_SOURCE,
    chunk_id,
    overview_chunk,
    overview_chunk_id,
    project_chunk,
)

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(
        self,
        repository: ProjectRepository,
        image_store: ImageStore,
        retriever: Optional[Retriever] = None,
    ) -> None:
        self._repository = repository
        self._image_store = image_store
        self._retriever = retriever
        self._indexed_fingerprint: Optional[str] = None

    def list_all(self) -> list[Project]:
        return self._repository.list_all()

    def replace_all(self, projects: Sequence[Project]) -> list[Project]:
        stored = self._repository.replace_all(projects)
        self._reindex(stored)
        return stored

    def store_image(self, content: bytes) -> str:
        return self._image_store.save(content)

    def load_image(self, name: str) -> Optional[bytes]:
        return self._image_store.load(name)

    def sync_index(self) -> None:
        """Indexes the catalog as it currently stands on disk.

        Must run at startup: the knowledge document holds no project, so on a
        fresh vector store the chatbot would otherwise know nothing about the
        projects until someone happened to save the catalog in the admin."""
        self._reindex(self.list_all())

    def sync_if_changed(self) -> None:
        """Reindexes when the catalog changed since this instance indexed it.

        With several instances (serverless), a save reaches only the one that
        handled it; the others notice here, before answering a question."""
        projects = self.list_all()
        if _fingerprint(projects) != self._indexed_fingerprint:
            self._reindex(projects)

    def _reindex(self, projects: Sequence[Project]) -> None:
        """Best-effort: the catalog is already persisted, so a retrieval
        hiccup must not look like a failed save to the user."""
        if self._retriever is None:
            return
        try:
            for lang in LANGS:
                keep_ids = [chunk_id(project.id, lang) for project in projects]
                if projects:
                    keep_ids.append(overview_chunk_id(lang))
                self._retriever.prune(lang, PROJECT_SOURCE, keep_ids)
                if projects:
                    chunks = [project_chunk(project, lang) for project in projects]
                    chunks.append(overview_chunk(projects, lang))
                    self._retriever.index(lang, chunks, PROJECT_SOURCE)
            self._indexed_fingerprint = _fingerprint(projects)
        except Exception:
            logger.exception("Projects saved, but syncing them to the retrieval index failed")


def _fingerprint(projects: Sequence[Project]) -> str:
    return hashlib.sha256(repr(list(projects)).encode("utf-8")).hexdigest()

