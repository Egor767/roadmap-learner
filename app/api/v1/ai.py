from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.dependencies.services import get_ai_service
from app.core.handlers import router_handler
from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    GenerateRequest,
    GenerateResponse,
    ModuleDistributeRequest,
    ModuleDistributeResponse,
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


@router.post("/chat", name="ai:chat", response_model=ChatResponse)
@router_handler
async def chat(
    payload: ChatRequest,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["AIService", Depends(get_ai_service)],
) -> ChatResponse:
    return await service.chat(user, payload)


@router.post(
    "/modules/distribute", name="ai:distribute_modules", response_model=ModuleDistributeResponse
)
@router_handler
async def distribute_modules(
    payload: ModuleDistributeRequest,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["AIService", Depends(get_ai_service)],
) -> ModuleDistributeResponse:
    return await service.distribute_modules(user, payload)


@router.post(
    "/questions/distribute",
    name="ai:distribute_questions",
    response_model=QuestionDistributeResponse,
)
@router_handler
async def distribute_questions(
    payload: QuestionDistributeRequest,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["AIService", Depends(get_ai_service)],
) -> QuestionDistributeResponse:
    return await service.distribute_questions(user, payload)


@router.post("/generate", name="ai:generate_entities", response_model=GenerateResponse)
@router_handler
async def generate_entities(
    payload: GenerateRequest,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["AIService", Depends(get_ai_service)],
) -> GenerateResponse:
    return await service.generate_entities(user, payload)
