"""Gemini-backed AnswerGenerator.

The model only ever sees the chunks retrieval selected, never the full
catalog. Its output goes through a JSON response schema so the answer comes
back as one clean field, with no preamble to strip."""

from datetime import date
from typing import Any, Optional, Sequence

from pydantic import BaseModel

from app.domain.models import Chunk, Engine, GeneratedAnswer, Lang


class _GeminiResponse(BaseModel):
    """Schema handed to Gemini for constrained decoding. It lives in the
    adapter, not the domain — it's a detail of how this provider is asked."""

    answer: str


SYSTEM_INSTRUCTION = (
    "Tu es l'assistant du portfolio d'Afdal Bouraima. Réponds UNIQUEMENT à partir du contexte fourni "
    "ci-dessous, jamais à partir de tes connaissances générales. Le contexte peut être hors sujet ou "
    "insuffisant (la recherche vectorielle est imparfaite) : dans ce cas, n'invente rien et ne réponds "
    "pas à une question sans rapport avec Afdal (recette de cuisine, météo, etc.). Dis simplement, en "
    "une phrase, que tu ne peux pas répondre à partir de son dossier, et propose de demander son "
    "parcours, ses projets, ses compétences ou sa disponibilité. "
    "Réponds dans la même langue que la question (français ou anglais). "
    "La date du jour est donnée avec la question : appuie-toi dessus pour les temps. Une expérience dont "
    "la date de fin est passée est terminée et se raconte au passé ; ne présente jamais Afdal comme "
    "travaillant encore à un poste terminé. "
    "Quand la question porte sur ses projets en général, cite tous les projets du contexte, en "
    "commençant par ceux présentés sur le site. "
    "Mise en forme : écris en Markdown. Si l'utilisateur demande un format (liste, tableau, résumé en "
    "une phrase, etc.), respecte-le. Sinon, choisis le format le plus lisible : une liste à puces pour "
    "énumérer plusieurs éléments (projets, expériences, compétences), un tableau pour comparer, une ou "
    "deux phrases pour une question simple. Mets en gras les éléments clés. N'utilise pas de titres (#). "
    "Reste concis. "
    "Ta réponse est affichée seule, sans carte ni composant à côté : elle doit se suffire à elle-même et "
    "citer concrètement les projets, entreprises ou technologies dont elle parle. "
    "Ne parle pas de toi ni de ton fonctionnement, sauf si l'on te demande comment fonctionne ce site "
    "ou cet assistant : réponds alors à partir du contexte. "
    "N'utilise jamais de tiret cadratin (—) : reformule avec une virgule, deux-points ou une nouvelle phrase."
)


def _strip_em_dashes(text: str) -> str:
    """Safety net behind the prompt rule: em dashes read as machine-written
    on a portfolio, and models don't always follow style instructions."""
    return text.replace(" — ", ", ").replace("—", ", ")


class GeminiAnswerGenerator:
    engine: Engine = "rag"

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._client: Optional[Any] = None

    def generate(self, question: str, lang: Lang, chunks: Sequence[Chunk]) -> GeneratedAnswer:
        from google.genai import types

        response = self._get_client().models.generate_content(
            model=self._model,
            contents=self._build_prompt(question, lang, chunks),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=_GeminiResponse,
            ),
        )
        parsed: _GeminiResponse = response.parsed
        # Sources and confidence are left to the chat service, which derives
        # them from retrieval rather than trusting the model's self-report.
        return GeneratedAnswer(
            text=_strip_em_dashes(parsed.answer),
            intent=chunks[0].category if chunks else "fallback",  # type: ignore[arg-type]
        )

    def _get_client(self) -> Any:
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _build_prompt(self, question: str, lang: Lang, chunks: Sequence[Chunk]) -> str:
        context = "\n".join(f"[{i + 1}] ({c.category}) {c.text}" for i, c in enumerate(chunks))
        # The model has no clock: without today's date it can't tell an
        # experience that ended from one still running.
        return f"Date du jour : {date.today().isoformat()}\n\nContexte:\n{context}\n\nQuestion ({lang}): {question}"
