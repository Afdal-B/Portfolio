from fastapi import APIRouter, Depends

from app.adapters.inbound.http import mappers
from app.adapters.inbound.http.dependencies import get_chat_service, limit_chat_rate
from app.adapters.inbound.http.schemas import ChatRequest, ChatResponse
from app.domain.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(limit_chat_rate)])


@router.post("", response_model=ChatResponse)
def post_chat(payload: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    return mappers.answer_to_dto(service.ask(payload.message, payload.lang))
