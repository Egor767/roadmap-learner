import uuid
from abc import ABC, abstractmethod
from typing import Optional, List

from app.schemas.user import UserInDB, UserFilters


class IUserRepository(ABC):
    @abstractmethod
    async def get_all_users(self) -> List[UserInDB]:
        pass

    @abstractmethod
    async def get_user_by_id(self, uid: uuid.UUID) -> Optional[UserInDB]: ...

    @abstractmethod
    async def get_users(self, filters: UserFilters) -> List[UserInDB]: ...

    @abstractmethod
    async def create_user(self, user_data: dict) -> UserInDB: ...

    @abstractmethod
    async def delete_user(self, uid: uuid.UUID) -> bool: ...

    @abstractmethod
    async def update_user(
        self, uid: uuid.UUID, user_data: dict
    ) -> Optional[UserInDB]: ...
