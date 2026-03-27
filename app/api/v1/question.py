from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.custom_types import BaseIdType
from app.core.dependencies.services import get_question_service
from app.core.handlers import router_handler
from app.schemas.question import (
    QuestionConfirmRequest,
    QuestionCreate,
    QuestionFilters,
    QuestionRead,
    QuestionUpdate,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services import QuestionService


router = APIRouter(
    prefix=settings.api.v1.questions,
    tags=["Questions"],
)


# -------------------------------------- GET ----------------------------------------------
@router.get("/filters", name="questions:filter_questions", response_model=list[QuestionRead])
@router_handler
async def get_questions(
    filters: Annotated[QuestionFilters, Depends()],
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["QuestionService", Depends(get_question_service)],
) -> list[QuestionRead]:
    return await service.get_by_filters(user, filters)


@router.get("/{id}", name="questions:question", response_model=QuestionRead)
@router_handler
async def get_question(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["QuestionService", Depends(get_question_service)],
) -> QuestionRead:
    return await service.get_by_id(user, id)


# -------------------------------------- CREATE --------------------------------------
@router.post("", name="questions:create_question", response_model=QuestionRead)
@router_handler
async def create_question(
    payload: QuestionCreate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["QuestionService", Depends(get_question_service)],
) -> QuestionRead:
    return await service.create(user, payload)


@router.post(
    "/batch",
    name="questions:create_batch_questions",
    response_model=list[QuestionRead],
    status_code=status.HTTP_201_CREATED,
)
@router_handler
async def confirm_questions(
    payload: QuestionConfirmRequest,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["QuestionService", Depends(get_question_service)],
) -> list[QuestionRead]:
    return await service.create_multiple(user, payload)


@router.post(
    "/{id}/link-card",
    name="questions:link_card",
)
@router_handler
async def link_card(
    id: BaseIdType,
    card_id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["QuestionService", Depends(get_question_service)],
):
    await service.link_concept(user, id, card_id)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{id}", name="questions:patch_question", response_model=QuestionRead)
@router_handler
async def update_question(
    id: BaseIdType,
    payload: QuestionUpdate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["QuestionService", Depends(get_question_service)],
) -> QuestionRead:
    return await service.update(user, id, payload)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{id}", name="questions:delete_question")
@router_handler
async def delete_question(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["QuestionService", Depends(get_question_service)],
) -> None:
    await service.delete(user, id)


@router.delete(
    "/{id}/unlink-card",
    name="questions:unlink-card",
)
@router_handler
async def unlink_card(
    id: BaseIdType,
    card_id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["QuestionService", Depends(get_question_service)],
):
    await service.unlink_concept(user, id, card_id)
