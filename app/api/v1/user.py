from typing import Annotated, TYPE_CHECKING, List

from fastapi import APIRouter, Depends

from core.authentication.fastapi_users import fastapi_users
from core.config import settings
from core.dependencies import get_users_db, get_user_service, get_user_filters
from core.handlers import router_handler
from schemas.user import UserRead, UserUpdate, UserFilters
from services import UserService

if TYPE_CHECKING:
    from models.user import SQLAlchemyUserDatabase

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)


@router.get(
    "",
    response_model=list[UserRead],
)
async def get_users(
    users_db: Annotated[
        "SQLAlchemyUserDatabase",
        Depends(get_users_db),
    ],
) -> list[UserRead]:
    users = await users_db.get_users()
    return [UserRead.model_validate(user) for user in users]


@router.get(
    "/filters",
    response_model=list[UserRead],
)
@router_handler
async def get_users_by_filters(
    filters: Annotated[
        UserFilters,
        Depends(),
    ],
    user_service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
):
    return await user_service.get_users(filters)


# /me
# /{id}
router.include_router(
    router=fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    ),
)
