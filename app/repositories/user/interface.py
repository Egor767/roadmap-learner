import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from app.schemas.user import UserInDB, UserCreate


class IUserRepository(ABC):

    @abstractmethod
    async def create_user(self, user: UserCreate) -> UserInDB:
        ...

    @abstractmethod
    async def get_user_by_id(self, uid: uuid.UUID) -> Optional[UserInDB]:
        ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        ...

    @abstractmethod
    async def update_user(self, uid: uuid.UUID, user_update: Dict[str, Any]) -> Optional[UserInDB]:
        ...

    @abstractmethod
    async def delete_user(self, uid: uuid.UUID) -> bool:
        ...

    @abstractmethod
    async def hard_delete_user(self, uid: uuid.UUID) -> bool:
        ...

