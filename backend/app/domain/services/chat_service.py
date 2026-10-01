"""Chat use case: turn a free-text question into an Answer.

Policy lives here; the how lives in adapters. Two AnswerGenerators are
injected — a primary one (the LLM, when configured) and a fallback one (the
scripted keyword router). The service decides when each runs:

- no primary generator at all          -> fallback
- retrieval too weak to be useful      -> generic "I answer from X" copy
- retrieval or primary generator raise -> fallback, so a flaky LLM or
                                          embedding API (quota, outage)
                                          never turns into a failed request
"""

import logging
from typing import Optional, Sequence

from app.domain.models import Answer, GeneratedAnswer, Lang, RetrievedChunk
from app.domain.ports import AnswerGenerator, CopyRepository, Retriever

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        fallback_generator: AnswerGenerator,
        copy: CopyRepository,
        primary_generator: Optional[AnswerGenerator] = None,
        retriever: Optional[Retriever] = None,
        top_k: int = 4,
        min_score: float = 0.12,
    ) -> None:
        self._fallback = fallback_generator
        self._copy = copy
        self._primary = primary_generator
        self._retriever = retriever
        self._top_k = top_k
        self._min_score = min_score

    def ask(self, message: str, lang: Lang) -> Answer:
        if self._primary is None or self._retriever is None:
            return self._run(self._fallback, message, lang, [])

        try:
            hits = self._retriever.search(message, lang, self._top_k)
        except Exception:
            logger.exception("Retrieval failed, falling back to the scripted generator")
            return self._run(self._fallback, message, lang, [])
        if not hits or hits[0].score < self._min_score:
            # Not worth an LLM call: nothing relevant enough was retrieved.
            return self._generic_fallback(lang)

        try:
            return self._run(self._primary, message, lang, hits)
        except Exception:
            logger.exception("Primary answer generator failed, falling back to the scripted one")
            return self._run(self._fallback, message, lang, [])

    def _run(
        self, generator: AnswerGenerator, message: str, lang: Lang, hits: Sequence[RetrievedChunk]
    ) -> Answer:
        generated = generator.generate(message, lang, [hit.chunk for hit in hits])
        return Answer(
            text=generated.text,
            sources=self._sources(generated, hits),
            confidence=self._confidence(generated, hits),
            intent=generated.intent,
            engine=generator.engine,
        )

    def _sources(self, generated: GeneratedAnswer, hits: Sequence[RetrievedChunk]) -> Optional[list[str]]:
        if generated.sources is not None:
            return generated.sources
        if not hits:
            return None
        unique: list[str] = []
        for hit in hits:
            if hit.chunk.source_label not in unique:
                unique.append(hit.chunk.source_label)
        return unique

    def _confidence(self, generated: GeneratedAnswer, hits: Sequence[RetrievedChunk]) -> Optional[int]:
        if generated.confidence is not None:
            return generated.confidence
        if not hits:
            return None
        # Retrieval similarity is a more honest confidence signal than asking
        # a language model to score itself.
        return max(0, min(100, round(hits[0].score * 100)))

    def _generic_fallback(self, lang: Lang) -> Answer:
        return Answer(
            text=self._copy.fallback_text(lang),
            sources=None,
            confidence=None,
            intent="fallback",
            engine="scripted",
        )
