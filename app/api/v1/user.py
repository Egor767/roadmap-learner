from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Request

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.dependencies.users import get_user_manager
from app.schemas.user import UserRead, UserUpdate

if TYPE_CHECKING:
    from app.models import User


router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)


# @router.get("", name="users:all_users", response_model=list[UserRead])
# async def get_users(
#     user_service: Annotated["UserService", Depends(get_user_service)],
# ) -> list[UserRead]:
#     return await user_service.get_all()
#
#
# @router.get("/filters", name="users:filter_users", response_model=list[UserRead])
# @router_handler
# async def get_users_by_filters(
#     filters: Annotated[UserFilters, Depends()],
#     current_user: Annotated["User", Depends(current_active_user)],
#     user_service: Annotated["UserService", Depends(get_user_service)],
# ):
#     return await user_service.get_by_filters(current_user, filters)


@router.get("/me", response_model=UserRead)
async def me(user: "User" = Depends(current_active_user)):
    """Return current authenticated user"""
    return UserRead.model_validate(user)


@router.patch("/me", response_model=UserRead)
async def update_me(
    request: Request,
    update: "UserUpdate",
    user: "User" = Depends(current_active_user),
    user_manager=Depends(get_user_manager),
):
    """Update current authenticated user"""
    updated = await user_manager.update(update, user, safe=True, request=request)
    return UserRead.model_validate(updated)
