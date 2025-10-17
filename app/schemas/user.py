from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class UserResponse(UserBase):
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    user_id: uuid.UUID
    username: str
    email: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserFilters(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None

    class Config:
        extra = "forbid"

