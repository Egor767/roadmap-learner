from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.dependencies.services import get_ai_service
from app.core.handlers import router_handler
from app.schemas.ai import (
    BlockDistributeRequest,
    BlockDistributeResponse,
    ChatRequest,
    ChatResponse,
    GenerateRequest,
    GenerateResponse,
    QuestionDistributeRequest,
    QuestionDistributeResponse,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services.ai import AIService


router = APIRouter(
    prefix=settings.api.v1.ai,
    tags=["AI"],
)


@router.post(
    "/chat",
    name="ai:chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
@router_handler
async def chat(
    request: ChatRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    ai_service: Annotated["AIService", Depends(get_ai_service)],
) -> ChatResponse:
    return await ai_service.chat(current_user, request)


@router.post(
    "/blocks/distribute",
    name="ai:distribute_blocks",
    response_model=BlockDistributeResponse,
    status_code=status.HTTP_200_OK,
)
@router_handler
async def distribute_blocks(
    request: BlockDistributeRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    ai_service: Annotated["AIService", Depends(get_ai_service)],
) -> BlockDistributeResponse:
    return await ai_service.distribute_blocks(current_user, request)


@router.post(
    "/questions/distribute",
    name="ai:distribute_questions",
    response_model=QuestionDistributeResponse,
    status_code=status.HTTP_200_OK,
)
@router_handler
async def distribute_questions(
    request: QuestionDistributeRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    ai_service: Annotated["AIService", Depends(get_ai_service)],
) -> QuestionDistributeResponse:
    return await ai_service.distribute_questions(current_user, request)


@router.post(
    "/generate",
    name="ai:generate_entities",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
)
@router_handler
async def generate_entities(
    request: GenerateRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    ai_service: Annotated["AIService", Depends(get_ai_service)],
) -> GenerateResponse:
    return await ai_service.generate_entities(current_user, request)
