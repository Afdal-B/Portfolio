"""Infrastructure configuration. Read here, injected into the domain as
plain values — no domain module ever imports this."""

from typing import Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # extra="ignore": backend/.env also holds values for the scripts (such as
    # PORTFOLIO_PROD_ADMIN_PASSWORD for make pull-projects). Rejecting them
    # would stop the server, and the error message would print their value.
    model_config = SettingsConfigDict(env_prefix="PORTFOLIO_", env_file=".env", extra="ignore")

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


    # Admin API (project editing without a redeploy). Unset = admin endpoints
    # are disabled entirely, so the feature is opt-in per deployment.
    admin_password: Optional[str] = None

    # Audience analytics on Upstash Redis. Also read under the names the
    # Vercel/Upstash integration sets. Unset: figures are kept in memory.
    upstash_redis_rest_url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "PORTFOLIO_UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_URL", "KV_REST_API_URL"
        ),
    )
    upstash_redis_rest_token: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "PORTFOLIO_UPSTASH_REDIS_REST_TOKEN", "UPSTASH_REDIS_REST_TOKEN", "KV_REST_API_TOKEN"
        ),
    )

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
