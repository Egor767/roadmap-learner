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
    session_service: Annotated["SessionService", Depends(get_session_service)],
) -> list[SessionRead]:
    return await session_service.get_all()


@router.get("/filters", name="sessions:filter_sessions", response_model=list[SessionRead])
@router_handler
async def get_sessions(
    filters: Annotated[SessionFilters, Depends()],
    current_user: Annotated["User", Depends(current_active_user)],
    session_service: Annotated["SessionService", Depends(get_session_service)],
) -> list[SessionRead]:
    return await session_service.get_by_filters(current_user, filters)


@router.get("/{session_id}", name="sessions:session", response_model=SessionRead)
@router_handler
async def get_session(
    session_id: BaseIdType,
    current_user: Annotated["User", Depends(current_active_user)],
    session_service: Annotated["SessionService", Depends(get_session_service)],
) -> SessionRead:
    return await session_service.get_by_id(current_user, session_id)


@router.get("/{session_id}/questions", name="sessions:questions", response_model=list[BaseIdType])
@router_handler
async def get_questions(
    session_id: BaseIdType,
    filters: Annotated[SessionQuestionFilter, Depends()],
    current_user: Annotated["User", Depends(current_active_user)],
    session_service: Annotated["SessionService", Depends(get_session_service)],
):
    return await session_service.get_session_questions(current_user, session_id, filters)


@router.get("/{session_id}/next-question", name="sessions:next_question", response_model=BaseIdType | None)
@router_handler
async def get_next_question(
    session_id: BaseIdType,
    current_user: Annotated["User", Depends(current_active_user)],
    session_service: Annotated["SessionService", Depends(get_session_service)],
) -> BaseIdType | None:
    return await session_service.get_next_question(current_user, session_id)


# -------------------------------------- CREATE --------------------------------------
@router.post("", name="sessions:create_session", response_model=SessionRead)
@router_handler
async def create_session(
    session_create_data: SessionCreate,
    current_user: Annotated["User", Depends(current_active_user)],
    session_service: Annotated["SessionService", Depends(get_session_service)],
) -> SessionRead:
    return await session_service.create(current_user, session_create_data)


@router.post("/{session_id}/answer", name="sessions:submit_answer")
@router_handler
async def submit_answer(
    session_id: BaseIdType,
    data: SessionItemCreate,
    background_tasks: BackgroundTasks,
    current_user: Annotated["User", Depends(current_active_user)],
    answer_service: Annotated["AnswerService", Depends(get_answer_service)],
):
    await answer_service.submit_answer(current_user, session_id, data, background_tasks)


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{session_id}", name="sessions:patch_session", response_model=SessionRead)
@router_handler
async def update_session(
    session_id: BaseIdType,
    session_update_data: SessionUpdate,
    current_user: Annotated["User", Depends(current_active_user)],
    session_service: Annotated["SessionService", Depends(get_session_service)],
) -> SessionRead:
    return await session_service.update(current_user, session_id, session_update_data)


@router.patch("/{session_id}/finish", name="sessions:finish_session", response_model=SessionFinishResult)
@router_handler
async def finish_session(
    session_id: BaseIdType,
    current_user: Annotated["User", Depends(current_active_user)],
    session_service: Annotated["SessionService", Depends(get_session_service)],
) -> SessionFinishResult:
    return await session_service.finish(current_user, session_id)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{session_id}", name="sessions:delete_session")
@router_handler
async def delete_session(
    session_id: BaseIdType,
    current_user: Annotated["User", Depends(current_active_user)],
    session_service: Annotated["SessionService", Depends(get_session_service)],
) -> None:
    await session_service.delete(current_user, session_id)
