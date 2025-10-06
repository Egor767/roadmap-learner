import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBaseModel(BaseModel):
    uid: uuid.UUID


class UserCreateModel(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdateModel(BaseModel):
    username: str | None = None
    email: EmailStr | None = None


class UserPresentModel(UserBaseModel):
    username: str
    email: str
    created_at: datetime
