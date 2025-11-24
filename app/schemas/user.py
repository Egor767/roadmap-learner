from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, ConfigDict

from app.core.types import BaseIdType


class UserRead(schemas.BaseUser[BaseIdType]):
    username: str | None = None


class UserCreate(schemas.BaseUserCreate):
    username: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = None


class UserFilters(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    is_active: str | None = None
    is_verified: str | None = None

    model_config = ConfigDict(extra="forbid")
