"""Analytics store on Upstash Redis, through its REST API: a plain HTTPS
call per operation, which suits serverless functions (no connection pool).

Figures are kept per day, in keys that expire on their own: daily counters
after 400 days, question texts after 90 days. Commands are sent as one
pipeline per operation to stay well within the free tier (500K commands a
month)."""

import json
from collections import Counter
from typing import Any, Sequence

import httpx

from app.adapters.outbound.analytics.memory_store import city_label
from app.domain.models import AnalyticsReport, DailyStats, QuestionEvent, VisitEvent

COUNTERS_TTL = 400 * 24 * 3600
QUESTIONS_TTL = 90 * 24 * 3600
MAX_QUESTIONS_PER_DAY = 500
PREFIX = "pf"


class UpstashAnalyticsStore:
    persistent = True

    def __init__(self, url: str, token: str, client: httpx.Client | None = None) -> None:
        self._url = url.rstrip("/")
        self._token = token
        self._client = client or httpx.Client(timeout=3.0)

    def record_visit(self, event: VisitEvent) -> None:
        day = event.day
        commands: list[list[Any]] = [
            ["INCR", f"{PREFIX}:pv:{day}"],
            ["PFADD", f"{PREFIX}:uv:{day}", event.visitor],
            ["HINCRBY", f"{PREFIX}:ref:{day}", event.referrer or "direct", 1],
        ]
        if event.country:
            commands.append(["HINCRBY", f"{PREFIX}:country:{day}", event.country, 1])
        if event.city:
            commands.append(["HINCRBY", f"{PREFIX}:city:{day}", city_label(event.city, event.country), 1])
        keys = {command[1] for command in commands}
        commands.extend(["EXPIRE", key, COUNTERS_TTL] for key in sorted(keys))
        self._pipeline(commands)

    def record_question(self, event: QuestionEvent) -> None:
        day = event.at[:10]
        commands: list[list[Any]] = [
            ["HINCRBY", f"{PREFIX}:q:{day}", event.outcome, 1],
            ["EXPIRE", f"{PREFIX}:q:{day}", COUNTERS_TTL],
        ]
        if event.text:
            key = f"{PREFIX}:ql:{day}"
            payload = {
                "at": event.at,
                "outcome": event.outcome,
                "text": event.text,
                "lang": event.lang,
                "confidence": event.confidence,
            }
            commands += [
                ["LPUSH", key, json.dumps(payload, ensure_ascii=False)],
                ["LTRIM", key, 0, MAX_QUESTIONS_PER_DAY - 1],
                ["EXPIRE", key, QUESTIONS_TTL],
            ]
        self._pipeline(commands)

    def report(self, days: Sequence[str], recent_limit: int) -> AnalyticsReport:
        per_day = 7
        commands: list[list[Any]] = []
        for day in days:
            commands += [
                ["GET", f"{PREFIX}:pv:{day}"],
                ["PFCOUNT", f"{PREFIX}:uv:{day}"],
                ["HGETALL", f"{PREFIX}:q:{day}"],
                ["HGETALL", f"{PREFIX}:country:{day}"],
                ["HGETALL", f"{PREFIX}:city:{day}"],
                ["HGETALL", f"{PREFIX}:ref:{day}"],
                ["LRANGE", f"{PREFIX}:ql:{day}", 0, recent_limit - 1],
            ]
        results = self._pipeline(commands)

        stats: list[DailyStats] = []
        countries: Counter[str] = Counter()
        cities: Counter[str] = Counter()
        referrers: Counter[str] = Counter()
        questions_by_day: list[list[QuestionEvent]] = []
        for index, day in enumerate(days):
            pv, uv, outcomes, country, city, ref, recent = results[index * per_day : (index + 1) * per_day]
            stats.append(
                DailyStats(day=day, page_views=int(pv or 0), visitors=int(uv or 0), questions=_hash(outcomes))
            )
            countries.update(_hash(country))
            cities.update(_hash(city))
            referrers.update(_hash(ref))
            questions_by_day.append([_question(raw) for raw in recent or []])

        recent_questions = [q for day_questions in reversed(questions_by_day) for q in day_questions]
        return AnalyticsReport(
            days=stats,
            countries=dict(countries),
            cities=dict(cities),
            referrers=dict(referrers),
            recent_questions=recent_questions[:recent_limit],
            persistent=self.persistent,
        )

    def _pipeline(self, commands: list[list[Any]]) -> list[Any]:
        response = self._client.post(
            f"{self._url}/pipeline",
            headers={"Authorization": f"Bearer {self._token}"},
            json=[[str(part) for part in command] for command in commands],
        )
        response.raise_for_status()
        results = []
        for item in response.json():
            if "error" in item:
                raise RuntimeError(f"Upstash error: {item['error']}")
            results.append(item.get("result"))
        return results


def _hash(flat: list[str] | None) -> dict[str, int]:
    """HGETALL comes back as a flat [field, value, field, value, ...] list."""
    if not flat:
        return {}
    return {flat[i]: int(flat[i + 1]) for i in range(0, len(flat), 2)}


def _question(raw: str) -> QuestionEvent:
    data = json.loads(raw)
    return QuestionEvent(
        at=data["at"],
        outcome=data["outcome"],
        text=data.get("text", ""),
        lang=data.get("lang", ""),
        confidence=data.get("confidence"),
    )
