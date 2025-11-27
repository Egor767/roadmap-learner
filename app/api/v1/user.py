from typing import Annotated, TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.core.authentication.fastapi_users import fastapi_users, current_active_user
from app.core.config import settings
from app.core.dependencies.services import get_user_service
from app.core.handlers import router_handler
from app.schemas.user import UserRead, UserUpdate, UserFilters

if TYPE_CHECKING:
    from app.models import User
    from app.services import UserService

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)


@router.get(
    "",
    name="users:all_users",
    response_model=list[UserRead],
)
async def get_users(
    user_service: Annotated[
        "UserService",
        Depends(get_user_service),
    ],
):
    return await user_service.get_all()


@router.get(
    "/filters",
    name="users:filter_users",
    response_model=list[UserRead],
)
@router_handler
async def get_users_by_filters(
    filters: Annotated[
        UserFilters,
        Depends(),
    ],
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    user_service: Annotated[
        "UserService",
        Depends(get_user_service),
    ],
):
    return await user_service.get_by_filters(
        current_user,
        filters,
    )


# /me
# /{id}
router.include_router(
    router=fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    ),
)
