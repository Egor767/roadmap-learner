from typing import Annotated, TYPE_CHECKING

from fastapi import APIRouter, Depends

from core.authentication.fastapi_users import fastapi_users
from core.config import settings
from core.dependencies import get_users_db
from schemas.user_manager import UserRead, UserUpdate

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
async def get_users_list(
    users_db: Annotated[
        "SQLAlchemyUserDatabase",
        Depends(get_users_db),
    ],
) -> list[UserRead]:
    users = await users_db.get_users()
    return [UserRead.model_validate(user) for user in users]


# /me
# /{id}
router.include_router(
    router=fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    ),
)
