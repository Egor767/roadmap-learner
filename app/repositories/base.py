from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.core.custom_types import BaseIdType
from app.models import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


# base.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseEntityRepository(ABC):
    """Base repository defining contract for entity data access"""

    def __init__(self, session: "AsyncSession"):
        self.session = session

    @abstractmethod
    async def get_all(self, user: BaseIdType) -> list[Base]:
        """Return all entities for user"""

    @abstractmethod
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Base]:
        """Return entities matching filters for user"""

    @abstractmethod
    async def get_by_id(self, target: BaseIdType, user: BaseIdType) -> Base:
        """Return entity by id verified against user"""

    @abstractmethod
    async def create(self, data: dict) -> Base:
        """Create and return new entity"""

    @abstractmethod
    async def update(self, target: BaseIdType, user: BaseIdType, data: dict) -> Base:
        """Update entity by id verified against user and return updated"""

    @abstractmethod
    async def delete(self, target: BaseIdType, user: BaseIdType) -> None:
        """Delete entity by id verified against user"""
