"""FastAPI dependencies: the bridge from HTTP to the composition root.

Routes depend on these rather than importing the container directly, so
tests can swap a service with `app.dependency_overrides` instead of
monkeypatching module globals."""

import secrets
from typing import Optional

from fastapi import Header, HTTPException, Request, status

from app.adapters.inbound.http import rate_limit
from app.container import container
from app.domain.services.analytics_service import AnalyticsService
from app.domain.services.chat_service import ChatService
from app.domain.services.content_service import ContentService
from app.domain.services.project_service import ProjectService


def get_chat_service() -> ChatService:
    return container.chat_service


def get_analytics_service() -> AnalyticsService:
    return container.analytics_service


# Sent by the site owner's browser (flagged from the admin page) so their
# own visits and questions don't skew the figures. Harmless if spoofed: it
# can only remove a visit from the statistics.
OWNER_HEADER = "x-pf-owner"


def is_owner(request: Request) -> bool:
    return request.headers.get(OWNER_HEADER) == "1"


_chat_limiter = rate_limit.SlidingWindowLimiter(
    max_requests=container.settings.chat_rate_limit_per_hour, window_seconds=3600
)


def limit_chat_rate(request: Request) -> None:
    def record_rejection() -> None:
        if not is_owner(request):
            container.analytics_service.record_question("limited")

    rate_limit.enforce(_chat_limiter, request, on_reject=record_rejection)


_visit_limiter = rate_limit.SlidingWindowLimiter(max_requests=60, window_seconds=3600)


def limit_visit_rate(request: Request) -> None:
    """Keeps one client from inflating the visit counters."""
    rate_limit.enforce(_visit_limiter, request)


# Every admin call counts, so a password can't be brute-forced: 120 attempts
# an hour is far above what the dashboard needs.
_admin_limiter = rate_limit.SlidingWindowLimiter(max_requests=120, window_seconds=3600)


def get_content_service() -> ContentService:
    return container.content_service


def get_project_service() -> ProjectService:
    return container.project_service


def require_admin(request: Request, authorization: Optional[str] = Header(default=None)) -> None:
    password = container.settings.admin_password
    if not password:
        # Same answer as an unknown route: a disabled admin API doesn't
        # reveal that it exists.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not Found")
    rate_limit.enforce(_admin_limiter, request)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing admin credentials")
    # Constant-time comparison so the endpoint doesn't leak the password
    # through response timing.
    if not secrets.compare_digest(authorization.removeprefix("Bearer "), password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid admin credentials")
