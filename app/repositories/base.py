from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

from app.core.types import BaseIdType

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(ABC):
    def __init__(self, session: "AsyncSession"):
        self.session = session

    @abstractmethod
    async def get_all(self) -> list[BaseModel] | list[None]:
        pass

    @abstractmethod
    async def get_by_filters(self, filters: BaseModel) -> list[BaseModel] | list[None]:
        pass

    @abstractmethod
    async def get_by_id(self) -> BaseModel | None:
        pass

    # @abstractmethod
    # async def get_by_parent(
    #     self, parent_id: BaseIdType, child_id: BaseIdType
    # ) -> BaseModel | None:
    #     pass

    @abstractmethod
    async def create(self, create_data: dict) -> BaseModel | None:
        pass

    @abstractmethod
    async def delete(self, object_id: BaseIdType) -> bool:
        pass

    @abstractmethod
    async def update(
        self,
        object_id: BaseIdType,
        update_data: BaseModel,
    ) -> BaseModel | None:
        pass
