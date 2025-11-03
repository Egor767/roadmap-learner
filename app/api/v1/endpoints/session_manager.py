import uuid
from typing import List

from fastapi import APIRouter, Depends
from starlette import status

from app.core.dependencies import get_session_manager_service
from app.core.handlers import router_handler
from app.schemas.session_manager import SessionResponse, SessionFilters, SessionCreate
from app.services.session_manager.service import SessionManagerService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/all", response_model=List[SessionResponse], status_code=status.HTTP_200_OK)
@router_handler
async def get_all_sessions(
    session_manager_service: SessionManagerService = Depends(get_session_manager_service)
):
    return await session_manager_service.get_all_sessions()


# -------------------------------------- GET ----------------------------------------------
@router.get("/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK)
@router_handler
async def get_user_session(
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    session_manager_service: SessionManagerService = Depends(get_session_manager_service)
):
    return await session_manager_service.get_user_session(user_id, session_id)


@router.get("/", response_model=List[SessionResponse])
async def get_user_sessions(
    user_id: uuid.UUID,  # = Depends(get_current_user)
    filters: SessionFilters = Depends(),
    session_manager_service: SessionManagerService = Depends(get_session_manager_service)
):
    return await session_manager_service.get_user_sessions(user_id, filters)


# -------------------------------------- CREATE --------------------------------------
@router.post("/", response_model=SessionResponse, status_code=201)
@router_handler
async def create_session(
    user_id: uuid.UUID,  # = Depends(get_current_user)
    session_create_data: SessionCreate,
    session_manager_service: SessionManagerService = Depends(get_session_manager_service)
):
    return await session_manager_service.create_session(user_id, session_create_data)

