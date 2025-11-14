from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from core.types import BaseIdType


class UserBase(BaseModel):
    username: Optional[str] = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: BaseIdType
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    id: BaseIdType
    username: Optional[str]
    email: EmailStr
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        from_attributes = True


class UserFilters(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

    class Config:
        extra = "forbid"
