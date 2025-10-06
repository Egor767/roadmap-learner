import uuid
from abc import ABC, abstractmethod
from app.schemas.user import UserCreateModel, UserBaseModel


class IUserRepository(ABC):

    @abstractmethod
    async def create_user(self, user_create_model: UserCreateModel) -> UserBaseModel:
        ...

    @abstractmethod
    async def get_user_by_id(self, uid: uuid.UUID) -> UserBaseModel:
        ...

