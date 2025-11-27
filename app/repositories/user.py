from typing import TYPE_CHECKING

from sqlalchemy import select

from app.core.handlers import repository_handler
from app.models import User
from app.repositories import BaseRepository

if TYPE_CHECKING:
    from app.core.types import BaseIdType


class UserRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[User]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        users = list(result.scalars().all())
        return users

    @repository_handler
    async def get_by_filters(self, filters: dict) -> list[User]:
        stmt = select(User)
        for field_name, value in filters.items():
            if value is not None:
                column = getattr(User, field_name, None)
                if column is not None:
                    stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        users = list(result.scalars().all())
        return users

    @repository_handler
    async def get_by_id(self, user_id: "BaseIdType") -> User | None:
        raise NotImplementedError("get_by_id() is not implemented for UserRepository")

    @repository_handler
    async def create(self, user_data: dict) -> User | None:
        raise NotImplementedError("create() is not implemented for UserRepository")

    @repository_handler
    async def update(self, user_id: "BaseIdType", data: dict) -> User | None:
        raise NotImplementedError("update() is not implemented for UserRepository")

    @repository_handler
    async def delete(self, user_id: "BaseIdType") -> bool:
        raise NotImplementedError("delete() is not implemented for UserRepository")
