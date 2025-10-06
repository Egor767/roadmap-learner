from abc import ABC, abstractmethod
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


class ISession(ABC):
    @abstractmethod
    async def create_engine(self):
        ...

    @abstractmethod
    async def create_tables(self):
        ...

    @abstractmethod
    async def drop_tables(self):
        ...

    @abstractmethod
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        ...

