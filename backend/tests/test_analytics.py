"""Audience analytics: the service's privacy rules, both stores, and the
HTTP endpoints that feed them."""

import json
from datetime import datetime, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from app.adapters.outbound.analytics.memory_store import InMemoryAnalyticsStore
from app.adapters.outbound.analytics.upstash_store import UpstashAnalyticsStore
from app.adapters.outbound.upstash import UpstashClient
from app.domain.models import QuestionEvent, VisitEvent
from app.domain.services.analytics_service import AnalyticsService
from app.main import app

BROWSER = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15"
client = TestClient(app)


def fixed_clock(day: int = 2):
    return lambda: datetime(2026, 10, day, 12, 0, tzinfo=timezone.utc)


def service(store=None, day: int = 2) -> tuple[AnalyticsService, InMemoryAnalyticsStore]:
    store = store or InMemoryAnalyticsStore()
    return AnalyticsService(store, "secret", clock=fixed_clock(day)), store


# --- service ------------------------------------------------------------


def test_same_visitor_counts_once_a_day_and_no_ip_is_kept() -> None:
    analytics, store = service()
    analytics.record_visit("203.0.113.7", BROWSER, "FR", "Lyon")
    analytics.record_visit("203.0.113.7", BROWSER, "FR", "Lyon")
    analytics.record_visit("198.51.100.2", BROWSER, "BE", "Bruxelles")

    day = analytics.report(1).days[0]
    assert (day.page_views, day.visitors) == (3, 2)
    assert "203.0.113.7" not in repr(store.__dict__)


def test_visitor_hash_changes_every_day() -> None:
    store = InMemoryAnalyticsStore()
    service(store, day=1)[0].record_visit("203.0.113.7", BROWSER)
    service(store, day=2)[0].record_visit("203.0.113.7", BROWSER)
    assert store._visitors["2026-10-01"].isdisjoint(store._visitors["2026-10-02"])


def test_bots_are_not_counted() -> None:
    analytics, _ = service()
    analytics.record_visit("203.0.113.7", "Googlebot/2.1 (+http://www.google.com/bot.html)")
    analytics.record_visit("203.0.113.7", "")
    assert analytics.report(1).days[0].page_views == 0


@pytest.mark.parametrize(
    "referrer,expected",
    [
        ("https://www.linkedin.com/feed/", "linkedin.com"),
        ("https://afdal-bouraima.fr/#projets", "direct"),
        ("https://afdal-portfolio-x.vercel.app/", "direct"),
        (None, "direct"),
    ],
)
def test_referrer_is_reduced_to_an_external_host(referrer, expected) -> None:
    analytics, _ = service()
    analytics.record_visit("203.0.113.7", BROWSER, referrer=referrer, site_host="afdal-bouraima.fr")
    assert analytics.report(1).referrers == {expected: 1}


def test_questions_are_counted_by_outcome_and_listed_newest_first() -> None:
    analytics, _ = service()
    analytics.record_question("rag", "Quels sont ses projets ?", "fr", 71)
    analytics.record_question("limited")
    analytics.record_question("scripted", "Son profil", "fr", 94)

    report = analytics.report(1)
    assert report.days[0].questions == {"rag": 1, "limited": 1, "scripted": 1}
    assert [q.text for q in report.recent_questions] == ["Son profil", "Quels sont ses projets ?"]


def test_a_failing_store_never_breaks_the_request() -> None:
    class BrokenStore(InMemoryAnalyticsStore):
        def record_visit(self, event):
            raise RuntimeError("Upstash is down")

    analytics, _ = service(BrokenStore())
    analytics.record_visit("203.0.113.7", BROWSER)  # no exception


# --- Upstash adapter ------------------------------------------------------


def upstash(handler) -> UpstashAnalyticsStore:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return UpstashAnalyticsStore(UpstashClient("https://example.upstash.io", "token", http=http))


def test_upstash_visit_is_one_pipeline_with_expiring_keys() -> None:
    sent = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/pipeline"
        assert request.headers["authorization"] == "Bearer token"
        sent.extend(json.loads(request.content))
        return httpx.Response(200, json=[{"result": 1} for _ in json.loads(request.content)])

    upstash(handler).record_visit(VisitEvent(day="2026-10-02", visitor="abc", country="FR", city="Lyon"))
    verbs = [command[0] for command in sent]
    assert verbs.count("EXPIRE") == 5
    assert ["HINCRBY", "pf:city:2026-10-02", "Lyon (FR)", "1"] in sent


def test_upstash_report_parses_redis_replies() -> None:
    question = json.dumps({"at": "2026-10-02T10:00:00+00:00", "outcome": "rag", "text": "Q ?", "lang": "fr"})

    def handler(request: httpx.Request) -> httpx.Response:
        replies = {
            "GET": "4",
            "PFCOUNT": 3,
            "HGETALL": ["FR", "2", "BE", "1"],
            "LRANGE": [question],
        }
        return httpx.Response(200, json=[{"result": replies[c[0]]} for c in json.loads(request.content)])

    report = upstash(handler).report(["2026-10-02"], recent_limit=10)
    assert (report.days[0].page_views, report.days[0].visitors) == (4, 3)
    assert report.countries == {"FR": 2, "BE": 1}
    assert report.recent_questions[0] == QuestionEvent(at="2026-10-02T10:00:00+00:00", outcome="rag", text="Q ?", lang="fr")
    assert report.persistent


# --- HTTP ---------------------------------------------------------------


def test_visit_endpoint_records_country_and_city_from_vercel_headers(offline_container) -> None:
    res = client.post(
        "/api/analytics/visit",
        json={"referrer": "https://github.com/Afdal-B"},
        headers={"user-agent": BROWSER, "x-vercel-ip-country": "FR", "x-vercel-ip-city": "Saint-%C3%89tienne"},
    )
    assert res.status_code == 204
    report = offline_container.analytics_service.report(1)
    assert report.countries == {"FR": 1}
    assert report.cities == {"Saint-Étienne (FR)": 1}
    assert report.referrers == {"github.com": 1}


def test_owner_visits_and_questions_are_not_recorded(offline_container) -> None:
    owner = {"user-agent": BROWSER, "x-pf-owner": "1"}
    client.post("/api/analytics/visit", json={}, headers=owner)
    client.post("/api/chat", json={"message": "voir les projets", "lang": "fr"}, headers=owner)
    report = offline_container.analytics_service.report(1)
    assert report.days[0].page_views == 0
    assert report.days[0].questions == {}


def test_chat_questions_are_recorded(offline_container) -> None:
    client.post("/api/chat", json={"message": "voir les projets", "lang": "fr"}, headers={"user-agent": BROWSER})
    question = offline_container.analytics_service.report(1).recent_questions[0]
    assert (question.text, question.outcome, question.confidence) == ("voir les projets", "scripted", 92)


def test_admin_stats_requires_the_password(offline_container) -> None:
    offline_container.settings.admin_password = "pw"
    assert client.get("/api/admin/stats").status_code == 401
    res = client.get("/api/admin/stats?days=7", headers={"Authorization": "Bearer pw"})
    assert res.status_code == 200
    assert len(res.json()["days"]) == 7
    assert res.json()["persistent"] is False


def test_catalog_editing_is_refused_on_vercel(offline_container, monkeypatch) -> None:
    offline_container.settings.admin_password = "pw"
    monkeypatch.setenv("VERCEL", "1")
    auth = {"Authorization": "Bearer pw"}
    assert client.get("/api/admin/capabilities", headers=auth).json() == {"projects_editable": False}
    assert client.put("/api/admin/projects", json=[], headers=auth).status_code == 409
