"""In-memory analytics store, for local development and tests. Figures
vanish on restart, which the admin dashboard points out."""

from collections import Counter, defaultdict
from typing import Sequence

from app.domain.models import AnalyticsReport, DailyStats, QuestionEvent, VisitEvent


class InMemoryAnalyticsStore:
    persistent = False

    def __init__(self) -> None:
        self._page_views: Counter[str] = Counter()
        self._visitors: dict[str, set[str]] = defaultdict(set)
        self._countries: dict[str, Counter[str]] = defaultdict(Counter)
        self._cities: dict[str, Counter[str]] = defaultdict(Counter)
        self._referrers: dict[str, Counter[str]] = defaultdict(Counter)
        self._outcomes: dict[str, Counter[str]] = defaultdict(Counter)
        self._questions: dict[str, list[QuestionEvent]] = defaultdict(list)

    def record_visit(self, event: VisitEvent) -> None:
        self._page_views[event.day] += 1
        self._visitors[event.day].add(event.visitor)
        if event.country:
            self._countries[event.day][event.country] += 1
        if event.city:
            self._cities[event.day][city_label(event.city, event.country)] += 1
        self._referrers[event.day][event.referrer or "direct"] += 1

    def record_question(self, event: QuestionEvent) -> None:
        day = event.at[:10]
        self._outcomes[day][event.outcome] += 1
        if event.text:
            self._questions[day].insert(0, event)

    def report(self, days: Sequence[str], recent_limit: int) -> AnalyticsReport:
        countries: Counter[str] = Counter()
        cities: Counter[str] = Counter()
        referrers: Counter[str] = Counter()
        recent: list[QuestionEvent] = []
        for day in days:
            countries.update(self._countries[day])
            cities.update(self._cities[day])
            referrers.update(self._referrers[day])
        for day in reversed(days):
            recent.extend(self._questions[day])
        return AnalyticsReport(
            days=[
                DailyStats(
                    day=day,
                    page_views=self._page_views[day],
                    visitors=len(self._visitors[day]),
                    questions=dict(self._outcomes[day]),
                )
                for day in days
            ],
            countries=dict(countries),
            cities=dict(cities),
            referrers=dict(referrers),
            recent_questions=recent[:recent_limit],
            persistent=self.persistent,
        )


def city_label(city: str, country: str | None) -> str:
    return f"{city} ({country})" if country else city
