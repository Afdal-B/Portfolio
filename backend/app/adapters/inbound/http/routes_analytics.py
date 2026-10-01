"""Visit beacon: the site sends one per page load. No cookie involved; the
visitor's IP is only used, hashed, inside the analytics service."""

from typing import Optional
from urllib.parse import unquote

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, Field

from app.adapters.inbound.http.dependencies import get_analytics_service, is_owner, limit_visit_rate
from app.adapters.inbound.http.rate_limit import client_key
from app.domain.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


class VisitIn(BaseModel):
    referrer: Optional[str] = Field(default=None, max_length=2000)


@router.post("/visit", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(limit_visit_rate)])
def post_visit(
    payload: VisitIn, request: Request, analytics: AnalyticsService = Depends(get_analytics_service)
) -> Response:
    if not is_owner(request):
        headers = request.headers
        analytics.record_visit(
            ip=client_key(request),
            user_agent=headers.get("user-agent", ""),
            # Set by Vercel from the visitor's IP; absent elsewhere.
            country=headers.get("x-vercel-ip-country"),
            city=unquote(headers.get("x-vercel-ip-city", "")),
            referrer=payload.referrer,
            site_host=headers.get("x-forwarded-host") or headers.get("host"),
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
