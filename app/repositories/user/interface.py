import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from app.schemas.user import UserInDB, UserCreate


class IUserRepository(ABC):

    @abstractmethod
    async def create_user(self, user: UserCreate) -> UserInDB:
        ...

    async def get_all_users(self) -> Optional[List[UserInDB]]:
        pass

    @abstractmethod
    async def get_user_by_id(self, uid: uuid.UUID) -> Optional[UserInDB]:
        ...

    @abstractmethod
    async def get_users_by_filters(self, filters) -> Optional[List[UserInDB]]:
        ...

    @abstractmethod
    async def delete_user(self, uid: uuid.UUID) -> bool:
        ...

    @abstractmethod
    async def update_user(self, uid: uuid.UUID, user_update: Dict[str, Any]) -> Optional[UserInDB]:
        ...

