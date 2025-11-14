from typing import List, Annotated

from fastapi import APIRouter, Depends, status

from core.config import settings
from core.dependencies import get_user_service
from core.handlers import router_handler
from core.types import BaseIdType
from schemas.user import UserCreate, UserResponse, UserFilters, UserUpdate
from services import UserService

router = APIRouter(
    prefix=settings.api.v1.users_service,
    tags=["Users Service"],
)


@router.get("/all", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
@router_handler
async def get_all_users(user_service: UserService = Depends(get_user_service)):
    return await user_service.get_all_users()


# -------------------------------------- GET --------------------------------------
@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
@router_handler
async def get_user_by_id(
    user_id: BaseIdType, user_service: Annotated[UserService, Depends(get_user_service)]
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
    user_data: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.create_user(user_data)


# -------------------------------------- DELETE --------------------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@router_handler
async def delete_user(
    current_user_id: BaseIdType,  # Depends(get_current_user)
    user_id: BaseIdType,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    await user_service.delete_user(current_user_id, user_id)
    return {"id": str(user_id), "status": "deleted"}


# -------------------------------------- UPDATE --------------------------------------
@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    current_user_id: BaseIdType,  # Depends(get_current_user)
    user_id: BaseIdType,  # query param
    user_data: UserUpdate,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.update_user(current_user_id, user_id, user_data)
