"""HTTP DTOs. Pydantic lives here, never in the domain — these describe the
wire format, which is free to differ from the domain model (localized
strings instead of bilingual maps, ...)."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

Lang = Literal["fr", "en"]
Intent = Literal[
    "profile", "avail", "projects", "skills", "experience", "nocv", "contact", "team", "fallback"
]
Engine = Literal["scripted", "rag"]


MAX_MESSAGE_LENGTH = 500


class ChatRequest(BaseModel):
    # Bounded because the message is embedded and forwarded to a quota-limited
    # LLM: an unbounded field lets any client burn the daily quota cheaply.
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    lang: Lang = "fr"


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[list[str]]
    confidence: Optional[int]
    intent: Intent
    # Which path actually produced this answer, so the UI can show whether
    # the model or the scripted fallback answered.
    engine: Engine


class ProjectOut(BaseModel):
    meta: str
    title: str
    result: str
    problem: str
    method: str
    stack: str
    metrics: str
    image_seed: str
    image_url: str
    screenshots: list[str]
    url: str
    summary: str
    code_url: str
    stack_items: list["SkillOut"]


class SkillOut(BaseModel):
    name: str
    icon: Optional[str]
    glyph: Optional[list[str]]


class ExperienceOut(BaseModel):
    company: str
    role: str
    contract_type: str
    period: str
    location: str
    context: str
    bullets: list[str]
    stack: list[SkillOut]


class SkillGroupOut(BaseModel):
    id: str
    title: str
    skills: list[SkillOut]


class ContactOut(BaseModel):
    key: str
    value: str
    href: str


class SuggestionOut(BaseModel):
    id: str
    label: str


class ProjectIn(BaseModel):
    """Admin payload: bilingual, unlike the public ProjectOut."""

    id: str = Field(default="")
    meta: dict[str, str]
    title: dict[str, str]
    result: dict[str, str]
    problem: dict[str, str]
    method: dict[str, str]
    stack: str
    metrics: dict[str, str]
    url: str = "#"
    image_url: str = ""
    screenshots: list[str] = Field(default_factory=list)
    image_seed: str = ""
    summary: dict[str, str] = Field(default_factory=dict)
    code_url: str = ""


class UploadResult(BaseModel):
    url: str


ProjectOut.model_rebuild()


class DailyStatsOut(BaseModel):
    day: str
    page_views: int
    visitors: int
    questions: dict[str, int]


class QuestionOut(BaseModel):
    at: str
    outcome: str
    text: str
    lang: str
    confidence: Optional[int]


class StatsOut(BaseModel):
    days: list[DailyStatsOut]
    countries: dict[str, int]
    cities: dict[str, int]
    referrers: dict[str, int]
    recent_questions: list[QuestionOut]
    persistent: bool


class AdminCapabilities(BaseModel):
    projects_editable: bool

