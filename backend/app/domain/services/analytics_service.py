"""Audience analytics: page visits and questions asked to the assistant.

Privacy by design, in line with the CNIL's exemption for audience
measurement: no cookie, and no IP address is ever stored. A visitor is
counted through a hash of their IP and browser salted with a secret and the
current day, so the same person is recognized within a day only, and the
hash can't be traced back to an address.

Recording is best effort: a storage failure is logged and swallowed, never
turned into a failed page load or chat answer."""

import hashlib
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional
from urllib.parse import urlparse

from app.domain.models import AnalyticsReport, QuestionEvent, QuestionOutcome, VisitEvent
from app.domain.ports import AnalyticsStore

logger = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 500

_BOT = re.compile(r"bot|crawl|spider|slurp|preview|headless|lighthouse|monitor", re.IGNORECASE)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AnalyticsService:
    def __init__(
        self,
        store: AnalyticsStore,
        secret: str,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._store = store
        self._secret = secret
        self._clock = clock

    def record_visit(
        self,
        ip: str,
        user_agent: str,
        country: Optional[str] = None,
        city: Optional[str] = None,
        referrer: Optional[str] = None,
        site_host: Optional[str] = None,
    ) -> None:
        """`site_host` is the host the visitor reached: a referrer on that
        same host is navigation within the site, not a referral."""
        if not user_agent or _BOT.search(user_agent):
            return
        day = self._clock().date().isoformat()
        visitor = hashlib.sha256(f"{self._secret}|{day}|{ip}|{user_agent}".encode("utf-8")).hexdigest()[:20]
        event = VisitEvent(
            day=day,
            visitor=visitor,
            country=(country or "").upper()[:2] or None,
            city=(city or "").strip()[:80] or None,
            referrer=_referrer_host(referrer, site_host),
        )
        self._safely(lambda: self._store.record_visit(event))

    def record_question(
        self,
        outcome: QuestionOutcome,
        text: str = "",
        lang: str = "",
        confidence: Optional[int] = None,
    ) -> None:
        event = QuestionEvent(
            at=self._clock().isoformat(timespec="seconds"),
            outcome=outcome,
            text=text.strip()[:MAX_QUESTION_LENGTH],
            lang=lang,
            confidence=confidence,
        )
        self._safely(lambda: self._store.record_question(event))

    def report(self, period_days: int, recent_limit: int = 200) -> AnalyticsReport:
        today = self._clock().date()
        days = [(today - timedelta(days=offset)).isoformat() for offset in range(period_days - 1, -1, -1)]
        return self._store.report(days, recent_limit)

    def _safely(self, action: Callable[[], None]) -> None:
        try:
            action()
        except Exception:
            logger.exception("Analytics recording failed")


def _referrer_host(referrer: Optional[str], site_host: Optional[str]) -> Optional[str]:
    """The referring site's host, or None for a direct visit."""
    if not referrer:
        return None
    host = (urlparse(referrer).hostname or "").lower().removeprefix("www.")
    own = (site_host or "").split(":")[0].lower().removeprefix("www.")
    if not host or host == own or host.endswith(".vercel.app") or host == "localhost":
        return None
    return host[:100]
