from abc import ABC, abstractmethod
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


class IDatabase(ABC):
    @abstractmethod
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]: ...

    @abstractmethod
    async def health_check(self) -> bool: ...
