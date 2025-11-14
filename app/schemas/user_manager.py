from typing import Optional

from fastapi_users import schemas

from core.types import BaseIdType


class UserRead(schemas.BaseUser[BaseIdType]):
    username: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    username: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str] = None
