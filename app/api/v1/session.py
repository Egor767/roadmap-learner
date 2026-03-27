import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.custom_types import BaseIdType
from app.core.dependencies.services import get_answer_service, get_session_service
from app.core.handlers import router_handler
from app.schemas.session import (
    SessionCreate,
    SessionFilters,
    SessionFinishResult,
    SessionItemCreate,
    SessionQuestionFilter,
    SessionRead,
    SessionUpdate,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services import AnswerService, SessionService

logger = logging.getLogger()

router = APIRouter(
    prefix=settings.api.v1.sessions,
    tags=["Sessions"],
)


# -------------------------------------- GET ----------------------------------------------
@router.get("", name="sessions:all_sessions", response_model=list[SessionRead])
@router_handler
async def get_all_sessions(
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["SessionService", Depends(get_session_service)],
) -> list[SessionRead]:
    return await service.get_all(user)


@router.get("/filters", name="sessions:filter_sessions", response_model=list[SessionRead])
@router_handler
async def get_sessions(
    filters: Annotated[SessionFilters, Depends()],
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["SessionService", Depends(get_session_service)],
) -> list[SessionRead]:
    return await service.get_by_filters(user, filters)


@router.get("/{id}", name="sessions:session", response_model=SessionRead)
@router_handler
async def get_session(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["SessionService", Depends(get_session_service)],
) -> SessionRead:
    return await service.get_by_id(user, id)


@router.get("/{id}/questions", name="sessions:questions", response_model=list[BaseIdType])
@router_handler
async def get_questions(
    id: BaseIdType,
    filters: Annotated[SessionQuestionFilter, Depends()],
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["SessionService", Depends(get_session_service)],
):
    return await service.get_session_questions(user, id, filters)


@router.get("/{id}/next-question", name="sessions:next_question", response_model=BaseIdType | None)
@router_handler
async def get_next_question(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["SessionService", Depends(get_session_service)],
) -> BaseIdType | None:
    return await service.get_next_question(user, id)


# -------------------------------------- CREATE --------------------------------------
@router.post("", name="sessions:create_session", response_model=SessionRead)
@router_handler
async def create_session(
    payload: SessionCreate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["SessionService", Depends(get_session_service)],
) -> SessionRead:
    return await service.create(user, payload)


@router.post("/{id}/answer", name="sessions:submit_answer")
@router_handler
async def submit_answer(
    id: BaseIdType,
    payload: SessionItemCreate,
    background_tasks: BackgroundTasks,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["AnswerService", Depends(get_answer_service)],
):
    await service.submit_answer(user, id, payload, background_tasks)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{id}", name="sessions:patch_session", response_model=SessionRead)
@router_handler
async def update_session(
    id: BaseIdType,
    payload: SessionUpdate,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["SessionService", Depends(get_session_service)],
) -> SessionRead:
    return await service.update(user, id, payload)


@router.patch("/{id}/finish", name="sessions:finish_session", response_model=SessionFinishResult)
@router_handler
async def finish_session(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["SessionService", Depends(get_session_service)],
) -> SessionFinishResult:
    return await service.finish(user, id)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{id}", name="sessions:delete_session")
@router_handler
async def delete_session(
    id: BaseIdType,
    user: Annotated["User", Depends(current_active_user)],
    service: Annotated["SessionService", Depends(get_session_service)],
) -> None:
    await service.delete(user, id)
