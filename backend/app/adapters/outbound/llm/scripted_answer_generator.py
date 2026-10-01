"""AnswerGenerator that needs no LLM: it routes the question to a scripted
Q&A entry by keyword.

Same port as the Gemini generator, so the chat service can use it as a
drop-in — either because no API key is configured, or because the LLM call
failed. It ignores the retrieved chunks and answers from its own canned
entries, which is why it supplies its own sources and confidence."""

from typing import Sequence

from app.domain import intent_router
from app.domain.models import Chunk, Engine, GeneratedAnswer, Lang
from app.domain.ports import CopyRepository, QARepository


class ScriptedAnswerGenerator:
    engine: Engine = "scripted"

    def __init__(self, qa: QARepository, copy: CopyRepository) -> None:
        self._qa = qa
        self._copy = copy

    def generate(self, question: str, lang: Lang, chunks: Sequence[Chunk]) -> GeneratedAnswer:
        intent = intent_router.route(question)
        entry = self._qa.get(intent) if intent != "fallback" else None

        if entry is None:
            return GeneratedAnswer(
                text=self._copy.fallback_text(lang),
                intent="fallback",
            )

        return GeneratedAnswer(
            text=entry.answer[lang],
            intent=entry.id,  # type: ignore[arg-type]
            sources=entry.sources[lang] if entry.sources else None,
            confidence=entry.confidence,
        )
