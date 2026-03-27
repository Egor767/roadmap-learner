from fastapi_users import schemas

from app.core.custom_types import BaseIdType


class UserRead(schemas.BaseUser[BaseIdType]):
    username: str | None = None


class UserCreate(schemas.BaseUserCreate):
    username: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = None
