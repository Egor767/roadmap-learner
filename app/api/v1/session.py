import logging

from typing import Annotated, TYPE_CHECKING

from fastapi import APIRouter, Depends, Request
from starlette import status

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.dependencies.services import get_session_service
from app.core.handlers import router_handler
from app.core.custom_types import BaseIdType
from app.schemas.session import (
    SessionRead,
    SessionCreate,
    SessionFilters,
    SessionResult,
    SessionUpdate,
    SessionCardsFilter,
)

if TYPE_CHECKING:
    from app.services import SessionService
    from app.models import User

logger = logging.getLogger()

router = APIRouter(
    prefix=settings.api.v1.sessions,
    tags=["Sessions"],
)


@router.get(
    "",
    name="sessions:all_sessions",
    response_model=list[SessionRead],
)
@router_handler
async def get_all_sessions(
    session_service: Annotated[
        "SessionService",
        Depends(get_session_service),
    ],
) -> list[SessionRead]:
    return await session_service.get_all()


# -------------------------------------- GET ----------------------------------------------
@router.get(
    "/filters",
    name="sessions:filter_sessions",
    response_model=list[SessionRead],
)
async def get_sessions(
    filters: Annotated[
        SessionFilters,
        Depends(),
    ],
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    session_service: Annotated[
        "SessionService",
        Depends(get_session_service),
    ],
) -> list[SessionRead]:
    return await session_service.get_by_filters(
        current_user,
        filters,
    )


@router.get(
    "/{session_id}",
    name="sessions:session",
    response_model=SessionRead,
)
@router_handler
async def get_session(
    session_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    session_service: Annotated[
        "SessionService",
        Depends(get_session_service),
    ],
) -> SessionRead:
    return await session_service.get_by_id(
        current_user,
        session_id,
    )


@router.get(
    "/{session_id}/cards",
)
@router_handler
async def get_cards(
    session_id: BaseIdType,
    filters: Annotated[
        SessionCardsFilter,
        Depends(),
    ],
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    session_service: Annotated[
        "SessionService",
        Depends(get_session_service),
    ],
):
    return await session_service.get_cards(
        current_user,
        session_id,
        filters,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "",
    name="sessions:create_session",
    response_model=SessionRead,
)
@router_handler
async def create_session(
    session_create_data: SessionCreate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    session_service: Annotated[
        "SessionService",
        Depends(get_session_service),
    ],
    request: Request,
):
    auth = request.headers.get("authorization")
    token = auth[7:]
    return await session_service.create(
        current_user,
        session_create_data,
        token,
    )


# -------------------------------------- DELETE --------------------------------------
@router.delete(
    "/{session_id}",
    name="sessions:delete_session",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router_handler
async def delete_session(
    session_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    session_service: Annotated[
        "SessionService",
        Depends(get_session_service),
    ],
) -> None:
    await session_service.delete(
        current_user,
        session_id,
    )


# -------------------------------------- UPDATE --------------------------------------
@router.patch(
    "/{session_id}",
    name="sessions:patch_session",
    response_model=SessionRead,
)
@router_handler
async def update_session(
    session_id: BaseIdType,
    session_update_data: SessionUpdate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    session_service: Annotated[
        "SessionService",
        Depends(get_session_service),
    ],
) -> SessionRead:
    return await session_service.update(
        current_user,
        session_id,
        session_update_data,
    )


@router.patch(
    "/{session_id}/finish",
    name="sessions:finish_session",
    response_model=SessionResult,
)
@router_handler
async def finish_session(
    session_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    session_service: Annotated[
        "SessionService",
        Depends(get_session_service),
    ],
) -> SessionResult:
    return await session_service.finish(
        current_user,
        session_id,
    )
