"""Domain models: plain dataclasses, no framework imports.

Bilingual fields are kept as `{"fr": ..., "en": ...}` maps — the domain holds
every language and leaves the choice of one to the presentation layer."""

from dataclasses import dataclass, field
from typing import Literal, Optional

Lang = Literal["fr", "en"]
Intent = Literal[
    "profile", "avail", "projects", "skills", "experience", "nocv", "contact", "team", "fallback"
]
Engine = Literal["scripted", "rag"]
Category = Literal["profile", "avail", "team", "contact", "projects", "skills", "experience"]

Localized = dict[str, str]


@dataclass(frozen=True)
class Project:
    id: str
    meta: Localized
    title: Localized
    result: Localized
    problem: Localized
    method: Localized
    stack: str
    metrics: Localized
    url: str = "#"
    image_url: str = ""
    screenshots: list[str] = field(default_factory=list)
    image_seed: str = ""
    # Short card blurb; falls back to `result` when empty.
    summary: Localized = field(default_factory=dict)
    # Source code or model page, shown next to the demo link.
    code_url: str = ""


@dataclass(frozen=True)
class Experience:
    company: str
    role: Localized
    contract_type: Localized
    period: Localized
    location: Localized
    context: Localized
    bullets: dict[str, list[str]]
    stack: list["Skill"]


@dataclass(frozen=True)
class Skill:
    name: str
    icon: Optional[str] = None
    glyph: Optional[list[str]] = None


@dataclass(frozen=True)
class SkillGroup:
    id: str
    title: Localized
    skills: list[Skill]


@dataclass(frozen=True)
class Contact:
    key: str
    value: str
    href: str


@dataclass(frozen=True)
class QAEntry:
    id: str
    question: Localized
    answer: Localized
    sources: Optional[dict[str, list[str]]] = None
    confidence: Optional[int] = None
    hidden: bool = False


@dataclass(frozen=True)
class Suggestion:
    id: str
    label: str


@dataclass(frozen=True)
class Chunk:
    """A retrievable passage of knowledge, whatever its source."""

    id: str
    lang: str
    category: Category
    text: str
    source_label: str


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float


@dataclass(frozen=True)
class GeneratedAnswer:
    """What an AnswerGenerator produces. `sources` and `confidence` are only
    set by generators that know them up front (the scripted one); the RAG
    path leaves them None so the chat service derives them from retrieval."""

    text: str
    intent: Intent
    sources: Optional[list[str]] = None
    confidence: Optional[int] = None


@dataclass(frozen=True)
class Answer:
    """The full result of asking a question — the chat use case's output."""

    text: str
    sources: Optional[list[str]]
    confidence: Optional[int]
    intent: Intent
    engine: Engine


# --- Audience analytics -------------------------------------------------

QuestionOutcome = Literal["rag", "scripted", "limited"]


@dataclass(frozen=True)
class VisitEvent:
    day: str  # ISO date, UTC
    visitor: str  # daily-salted hash: identifies a visitor for one day only
    country: Optional[str] = None  # ISO 3166-1 alpha-2
    city: Optional[str] = None
    referrer: Optional[str] = None  # host of the referring site, None = direct


@dataclass(frozen=True)
class QuestionEvent:
    at: str  # ISO datetime, UTC
    outcome: QuestionOutcome
    text: str = ""  # empty when the question never reached the assistant
    lang: str = ""
    confidence: Optional[int] = None


@dataclass(frozen=True)
class DailyStats:
    day: str
    page_views: int
    visitors: int
    questions: dict[str, int]  # by outcome


@dataclass(frozen=True)
class AnalyticsReport:
    days: list[DailyStats]
    countries: dict[str, int]
    cities: dict[str, int]
    referrers: dict[str, int]
    recent_questions: list[QuestionEvent]
    persistent: bool  # False: in-memory store, figures vanish on restart
