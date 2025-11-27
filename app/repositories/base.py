from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.types import BaseIdType
    from app.models import Base


class BaseRepository(ABC):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    @abstractmethod
    async def get_all(self) -> list["Base"]:
        pass

    @abstractmethod
    async def get_by_filters(self, filters: dict) -> list["Base"]:
        pass

    @abstractmethod
    async def get_by_id(self, object_id: "BaseIdType") -> "Base" | None:
        pass

    @abstractmethod
    async def create(self, create_data: dict) -> "Base" | None:
        pass

    @abstractmethod
    async def delete(self, object_id: "BaseIdType") -> bool:
        pass

    @abstractmethod
    async def update(self, object_id: "BaseIdType", update_data: dict) -> "Base" | None:
        pass
