"""Infrastructure configuration. Read here, injected into the domain as
plain values — no domain module ever imports this."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PORTFOLIO_", env_file=".env")

    allowed_origins: list[str] = ["http://localhost:5173"]

    # Unset gemini_api_key keeps the chat on the scripted keyword generator —
    # useful for offline dev and tests.
    gemini_api_key: Optional[str] = None
    # "Flash Lite" free-tier daily quota is far more generous than the full
    # "Flash" models (500 requests/day vs 20/day as of writing).
    gemini_model: str = "gemini-3.5-flash-lite"
    # Embeddings come from the same Gemini API key. gemini-embedding-001 takes
    # several texts per call and a task type (document vs query).
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 768

    # Where ChromaDB keeps its index. Unset: backend/.chroma locally, /tmp on
    # Vercel, whose functions can only write there.
    chroma_path: Optional[str] = None

    # Admin API (project editing without a redeploy). Unset = admin endpoints
    # are disabled entirely, so the feature is opt-in per deployment.
    admin_password: Optional[str] = None

    # Questions allowed per visitor per hour on the chat endpoint.
    chat_rate_limit_per_hour: int = 20

    rag_top_k: int = 6
    # Kept low on purpose: with this small a corpus and a general-purpose
    # multilingual model, similarity scores for legitimately relevant
    # questions can land lower than scores for unrelated small talk. This
    # threshold only guards against burning an API call on pure noise;
    # judging relevance (including answering "fallback") is left to the LLM.
    rag_min_score: float = 0.12


settings = Settings()
