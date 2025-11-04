import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_user_service
from app.core.handlers import router_handler
from app.schemas.user import UserCreate, UserResponse, UserFilters, UserUpdate
from app.services.user.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/all", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
@router_handler
async def get_all_users(user_service: UserService = Depends(get_user_service)):
    return await user_service.get_all_users()


# -------------------------------------- GET --------------------------------------
@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
@router_handler
async def get_user_by_id(
    user_id: uuid.UUID, user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_user_by_id(user_id)


@router.get("/", response_model=List[UserResponse])
@router_handler
async def get_users(
    filters: UserFilters = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_users(filters)


# -------------------------------------- CREATE --------------------------------------
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router_handler
async def create_user(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_data)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@router_handler
async def delete_user(
    current_user_id: uuid.UUID,  # Depends(get_current_user)
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_user(current_user_id, user_id)
    return {"id": str(user_id), "status": "deleted"}


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    current_user_id: uuid.UUID,  # Depends(get_current_user)
    user_id: uuid.UUID,  # query param
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(current_user_id, user_id, user_data)
