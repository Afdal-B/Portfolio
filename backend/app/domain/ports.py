"""Ports: the interfaces the domain needs from the outside world.

Everything here is declared in the domain's own vocabulary and implemented
by adapters (app/adapters/outbound/...). The domain never imports an adapter;
the composition root (app/container.py) wires them together."""

from typing import Optional, Protocol, Sequence

from app.domain.models import (
    AnalyticsReport,
    Chunk,
    Contact,
    Engine,
    Experience,
    GeneratedAnswer,
    Lang,
    Project,
    QAEntry,
    QuestionEvent,
    RetrievedChunk,
    Skill,
    SkillGroup,
    VisitEvent,
)


class ProjectRepository(Protocol):
    def list_all(self) -> list[Project]: ...

    def replace_all(self, projects: Sequence[Project]) -> list[Project]: ...


class ExperienceRepository(Protocol):
    def list_all(self) -> list[Experience]: ...


class SkillRepository(Protocol):
    def list_all(self) -> list[SkillGroup]: ...

    def resolve(self, name: str) -> Skill:
        """The catalog entry for a technology named in free text (a project's
        stack), or a bare Skill without icon when the catalog doesn't know it."""
        ...


class ContactRepository(Protocol):
    def list_all(self) -> list[Contact]: ...


class QARepository(Protocol):
    def list_all(self) -> list[QAEntry]:
        """Scripted entries, in display order."""
        ...

    def get(self, entry_id: str) -> Optional[QAEntry]: ...


class CopyRepository(Protocol):
    def fallback_text(self, lang: Lang) -> str: ...


class KnowledgeRepository(Protocol):
    """Source of the hand-written knowledge passages (the CV/bio document)."""

    def chunks(self, lang: Lang) -> list[Chunk]: ...


class Embedder(Protocol):
    """Turns text into vectors. Documents and questions are embedded
    differently: retrieval models encode the two roles asymmetrically."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class Retriever(Protocol):
    """Semantic search over indexed chunks, plus the indexing side of it."""

    def search(self, query: str, lang: Lang, top_k: int) -> list[RetrievedChunk]: ...

    def index(self, lang: Lang, chunks: Sequence[Chunk], source: str) -> None: ...

    def prune(self, lang: Lang, source: str, keep_ids: Sequence[str]) -> None:
        """Drops chunks of `source` whose id is no longer in `keep_ids`."""
        ...


class AnswerGenerator(Protocol):
    engine: Engine

    def generate(self, question: str, lang: Lang, chunks: Sequence[Chunk]) -> GeneratedAnswer: ...


class ImageStore(Protocol):
    def save(self, content: bytes) -> str:
        """Stores an image and returns the URL it is served from."""
        ...

    def load(self, name: str) -> Optional[bytes]:
        """The stored image with that file name, or None."""
        ...


class AnalyticsStore(Protocol):
    """Where audience figures are kept. Never holds an IP address: visits
    arrive already anonymized."""

    persistent: bool

    def record_visit(self, event: VisitEvent) -> None: ...

    def record_question(self, event: QuestionEvent) -> None: ...

    def report(self, days: Sequence[str], recent_limit: int) -> AnalyticsReport: ...
