import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db_session, get_user_service
from app.core.handlers import router_handler
from app.schemas.user import UserBase, UserCreate, UserResponse
from app.services.user.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
@router_handler
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_data)

