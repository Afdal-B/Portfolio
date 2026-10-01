"""Chat use case on the scripted path — no LLM, no retriever injected."""

import pytest

from app.container import container


@pytest.fixture
def service(offline_container):
    return offline_container.chat_service


@pytest.mark.parametrize(
    "question,expected_intent,expected_confidence",
    [
        ("Voir les projets", "projects", 92),
        ("Compétences", "skills", 85),
        ("Disponibilité & CDI", "avail", 99),
        ("Travaille-t-il avec des non-tech ?", "team", 82),
    ],
)
def test_answer_confidence_and_intent(service, question, expected_intent, expected_confidence) -> None:
    answer = service.ask(question, "fr")
    assert answer.intent == expected_intent
    assert answer.confidence == expected_confidence
    assert answer.sources


def test_answer_contact_has_no_trace(service) -> None:
    answer = service.ask("Me contacter", "fr")
    assert answer.intent == "contact"
    assert answer.confidence is None
    assert answer.sources is None


def test_answer_nocv_has_no_trace(service) -> None:
    answer = service.ask("Le CV est-il téléchargeable ?", "fr")
    assert answer.intent == "nocv"
    assert answer.confidence is None


def test_answer_fallback(service) -> None:
    answer = service.ask("asdkjasdkjasd", "fr")
    assert answer.intent == "fallback"
    assert answer.confidence is None
    assert answer.sources is None
    assert answer.text


def test_answer_respects_lang(service) -> None:
    fr = service.ask("Voir les projets", "fr")
    en = service.ask("See the projects", "en")
    assert fr.text != en.text
    assert fr.intent == en.intent == "projects"


def test_engine_is_scripted_without_an_llm(service) -> None:
    assert service.ask("Voir les projets", "fr").engine == "scripted"


def test_confidence_bar_fixtures(service) -> None:
    # round(conf/20) out of 5 bars, per the trace-panel spec.
    fixtures = {
        "Son profil en une phrase": 94,
        "Disponibilité & CDI": 99,
        "Voir les projets": 92,
        "Compétences": 85,
        "Travaille-t-il avec des non-tech ?": 82,
    }
    expected_bars = {94: 5, 99: 5, 92: 5, 85: 4, 82: 4}
    for question, confidence in fixtures.items():
        answer = service.ask(question, "fr")
        assert answer.confidence == confidence
        assert round(confidence / 20) == expected_bars[confidence]


def test_container_builds_no_retriever_without_an_api_key() -> None:
    assert container.retriever is None
    assert container.primary_generator is None
