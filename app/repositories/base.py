from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.models import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseEntityRepository(ABC):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    @abstractmethod
    async def get_all(self) -> list[Base]:
        pass

    @abstractmethod
    async def get_by_filters(self, filters: dict) -> list[Base]:
        pass

    @abstractmethod
    async def get_by_id(self, target: BaseIdType) -> Base:
        pass

    @abstractmethod
    async def create(self, data: dict) -> Base:
        pass

    @abstractmethod
    async def update(self, target: BaseIdType, data: dict) -> Base:
        pass

    @abstractmethod
    async def delete(self, target: BaseIdType) -> Base | None:
        pass
