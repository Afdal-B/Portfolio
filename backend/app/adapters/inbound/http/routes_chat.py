from fastapi import APIRouter, Depends, Request

from app.adapters.inbound.http import mappers
from app.adapters.inbound.http.dependencies import (
    get_analytics_service,
    get_chat_service,
    is_owner,
    limit_chat_rate,
)
from app.adapters.inbound.http.schemas import ChatRequest, ChatResponse
from app.domain.services.analytics_service import AnalyticsService
from app.domain.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(limit_chat_rate)])


@router.post("", response_model=ChatResponse)
def post_chat(
    payload: ChatRequest,
    request: Request,
    service: ChatService = Depends(get_chat_service),
    analytics: AnalyticsService = Depends(get_analytics_service),
) -> ChatResponse:
    answer = service.ask(payload.message, payload.lang)
    if not is_owner(request):
        analytics.record_question(answer.engine, payload.message, payload.lang, answer.confidence)
    return mappers.answer_to_dto(answer)
