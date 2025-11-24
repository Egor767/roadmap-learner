from typing import List, Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.core.config import settings
from app.core.dependencies.services import get_session_manager_service
from app.core.handlers import router_handler
from app.core.types import BaseIdType
from app.schemas.card import CardRead
from app.schemas.session import (
    SessionResponse,
    SessionFilters,
    SessionCreate,
    SessionResult,
    SubmitAnswerRequest,
)
from app.services import SessionManagerService

router = APIRouter(
    prefix=settings.api.v1.sessions,
    tags=["Sessions"],
)


@router.get(
    "/all",
    response_model=List[SessionResponse],
    status_code=status.HTTP_200_OK,
)
@router_handler
async def get_all_sessions(
    session_manager_service: Annotated[
        SessionManagerService,
        Depends(get_session_manager_service),
    ],
):
    return await session_manager_service.get_all_sessions()


# -------------------------------------- GET ----------------------------------------------
@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
)
@router_handler
async def get_user_session(
    user_id: BaseIdType,
    session_id: BaseIdType,
    session_manager_service: Annotated[
        SessionManagerService,
        Depends(get_session_manager_service),
    ],
):
    return await session_manager_service.get_user_session(
        user_id,
        session_id,
    )


@router.get("/", response_model=List[SessionResponse])
async def get_user_sessions(
    user_id: BaseIdType,  # = Depends(get_current_user)
    filters: Annotated[
        SessionFilters,
        Depends(),
    ],
    session_manager_service: Annotated[
        SessionManagerService,
        Depends(get_session_manager_service),
    ],
):
    return await session_manager_service.get_user_sessions(
        user_id,
        filters,
    )


@router.get(
    "/{session_id}/next-card",
    response_model=CardRead,
)
@router_handler
async def get_next_card(
    user_id: BaseIdType,
    session_id: BaseIdType,
    session_manager_service: Annotated[
        SessionManagerService,
        Depends(get_session_manager_service),
    ],
):
    return await session_manager_service.get_next_card(
        user_id,
        session_id,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "/",
    response_model=SessionResponse,
    status_code=201,
)
@router_handler
async def create_session(
    user_id: BaseIdType,  # = Depends(get_current_user)
    session_create_data: SessionCreate,
    session_manager_service: Annotated[
        SessionManagerService,
        Depends(get_session_manager_service),
    ],
):
    return await session_manager_service.create_session(
        user_id,
        session_create_data,
    )


# -------------------------------------- UPDATE --------------------------------------
# finish session
@router.patch(
    "/{session_id}/finish",
    response_model=SessionResult,
)
@router_handler
async def finish_session(
    user_id: BaseIdType,  # = Depends(get_current_user)
    session_id: BaseIdType,
    session_manager_service: Annotated[
        SessionManagerService,
        Depends(get_session_manager_service),
    ],
):
    return await session_manager_service.finish_session(
        user_id,
        session_id,
    )


@router.patch(
    "/{session_id}/abandon",
    status_code=status.HTTP_200_OK,
)
@router_handler
async def abandon_session(
    user_id: BaseIdType,
    session_id: BaseIdType,
    session_manager_service: Annotated[
        SessionManagerService,
        Depends(get_session_manager_service),
    ],
):
    success = await session_manager_service.abandon_session(
        user_id,
        session_id,
    )
    return {"successful": success}


# submit answer
@router.patch(
    "/{session_id}/answer",
    response_model=SessionResponse,
)
@router_handler
async def submit_answer(
    user_id: BaseIdType,
    session_id: BaseIdType,
    answer_data: SubmitAnswerRequest,
    session_manager_service: Annotated[
        SessionManagerService,
        Depends(get_session_manager_service),
    ],
):
    return await session_manager_service.submit_answer(
        user_id,
        session_id,
        answer_data,
    )


# -------------------------------------- DELETE --------------------------------------
@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router_handler
async def delete_block(
    user_id: BaseIdType,  # = Depends(get_current_user)
    session_id: BaseIdType,
    session_manager_service: Annotated[
        SessionManagerService,
        Depends(get_session_manager_service),
    ],
):
    success = await session_manager_service.delete_session(
        user_id,
        session_id,
    )

    return {"successful": success}
