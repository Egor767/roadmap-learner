import uuid
from abc import ABC

from app.repositories.user.interface import IUserRepository
from app.schemas.user import UserCreateModel, UserBaseModel
from app.services.user.interface import IUserService


class UserService(IUserService):
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    async def create_user(self, user_create_model: UserCreateModel) -> UserBaseModel:
        ...
        return await self.repo.create_user(user_create_model)

    async def get_user_by_id(self, uid: uuid.UUID) -> UserBaseModel:
        ...
        return await self.repo.get_user_by_id(uid)
