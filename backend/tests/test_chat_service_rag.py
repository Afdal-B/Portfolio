"""Chat use case on the RAG path. Ports are injected as fakes here — no
monkeypatching, no network, no embedding model."""

from typing import Sequence

import pytest

from app.domain.models import Chunk, Engine, GeneratedAnswer, RetrievedChunk
from app.domain.services.chat_service import ChatService


def chunk(id_: str, label: str, category: str = "projects") -> Chunk:
    return Chunk(id=id_, lang="fr", category=category, text=f"contenu {id_}", source_label=label)


class FakeRetriever:
    def __init__(self, hits: Sequence[RetrievedChunk], error: Exception = None) -> None:
        self._hits = list(hits)
        self._error = error
        self.indexed: list[tuple] = []

    def search(self, query, lang, top_k):
        if self._error:
            raise self._error
        return self._hits[:top_k]

    def index(self, lang, chunks, source):
        self.indexed.append((lang, list(chunks), source))

    def prune(self, lang, source, keep_ids):
        pass


class FakeGenerator:
    def __init__(self, engine: Engine, answer: GeneratedAnswer = None, error: Exception = None) -> None:
        self.engine = engine
        self._answer = answer
        self._error = error
        self.calls = 0

    def generate(self, question, lang, chunks):
        self.calls += 1
        if self._error:
            raise self._error
        return self._answer


class FakeCopy:
    def fallback_text(self, lang):
        return "Je réponds à partir du dossier d'Afdal…"


def build(primary=None, retriever=None, fallback=None, min_score=0.12):
    return ChatService(
        fallback_generator=fallback
        or FakeGenerator("scripted", GeneratedAnswer(text="scripté", intent="projects", confidence=92)),
        copy=FakeCopy(),
        primary_generator=primary,
        retriever=retriever,
        min_score=min_score,
    )


def test_rag_path_derives_sources_and_confidence_from_retrieval() -> None:
    hits = [
        RetrievedChunk(chunk=chunk("a", "Assistant documentaire interne"), score=0.82),
        RetrievedChunk(chunk=chunk("b", "Assistant documentaire interne"), score=0.6),  # duplicate label
    ]
    primary = FakeGenerator("rag", GeneratedAnswer(text="Réponse du LLM.", intent="projects"))

    answer = build(primary=primary, retriever=FakeRetriever(hits)).ask("parle-moi des projets", "fr")

    assert answer.text == "Réponse du LLM."
    assert answer.intent == "projects"
    assert answer.confidence == 82  # top score, not self-reported
    assert answer.sources == ["Assistant documentaire interne"]  # deduplicated
    assert answer.engine == "rag"


def test_weak_retrieval_skips_the_llm_entirely() -> None:
    primary = FakeGenerator("rag", GeneratedAnswer(text="jamais appelé", intent="profile"))
    hits = [RetrievedChunk(chunk=chunk("a", "Dispo"), score=0.05)]

    answer = build(primary=primary, retriever=FakeRetriever(hits), min_score=0.12).ask("bla bla", "fr")

    assert primary.calls == 0
    assert answer.intent == "fallback"
    assert answer.engine == "scripted"
    assert answer.confidence is None
    assert answer.sources is None


def test_generator_failure_falls_back_to_the_scripted_one() -> None:
    primary = FakeGenerator("rag", error=RuntimeError("Gemini is down"))
    fallback = FakeGenerator(
        "scripted", GeneratedAnswer(text="scripté", intent="projects", confidence=92)
    )
    hits = [RetrievedChunk(chunk=chunk("a", "Projets"), score=0.9)]

    answer = build(primary=primary, retriever=FakeRetriever(hits), fallback=fallback).ask("voir les projets", "fr")

    assert primary.calls == 1
    assert fallback.calls == 1
    assert answer.intent == "projects"
    assert answer.confidence == 92
    assert answer.engine == "scripted"


def test_without_a_primary_generator_only_the_fallback_runs() -> None:
    fallback = FakeGenerator(
        "scripted", GeneratedAnswer(text="scripté", intent="projects", confidence=92)
    )

    answer = build(primary=None, retriever=None, fallback=fallback).ask("voir les projets", "fr")

    assert fallback.calls == 1
    assert answer.engine == "scripted"


@pytest.mark.parametrize("score,expected", [(1.0, 100), (0.5, 50), (0.0, 0)])
def test_confidence_is_the_top_score_as_a_percentage(score, expected) -> None:
    primary = FakeGenerator("rag", GeneratedAnswer(text="x", intent="profile"))
    hits = [RetrievedChunk(chunk=chunk("a", "A"), score=score)]

    answer = build(primary=primary, retriever=FakeRetriever(hits), min_score=-1).ask("q", "fr")

    assert answer.confidence == expected


def test_retrieval_failure_falls_back_to_the_scripted_one() -> None:
    # e.g. the embedding API answering 429 (quota) for the question.
    primary = FakeGenerator("rag", GeneratedAnswer(text="jamais appelé", intent="profile"))
    retriever = FakeRetriever([], error=RuntimeError("429 RESOURCE_EXHAUSTED"))

    answer = build(primary=primary, retriever=retriever).ask("voir les projets", "fr")

    assert primary.calls == 0
    assert answer.engine == "scripted"
    assert answer.text == "scripté"
