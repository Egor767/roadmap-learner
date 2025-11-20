from typing import TYPE_CHECKING

from sqlalchemy import select

from core.handlers import repository_handler
from models import User
from repositories import BaseRepository
from schemas.user import UserFilters
from schemas.user import UserRead

if TYPE_CHECKING:
    from core.types import BaseIdType


def map_to_schema(db_user: User | None) -> UserRead | None:
    if db_user:
        return UserRead.model_validate(db_user)
    return


class UserRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[UserRead]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [map_to_schema(user) for user in users]

    @repository_handler
    async def get_by_filters(self, filters: UserFilters) -> list[UserRead]:
        stmt = select(User)

        if filters.email is not None:
            stmt = stmt.where(User.email == filters.email)
        if filters.username is not None:
            stmt = stmt.where(User.username == filters.username)

        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [map_to_schema(user) for user in users]

    @repository_handler
    async def get_by_id(self, user_id: "BaseIdType") -> UserRead | None:
        raise NotImplementedError("get_by_id() is not implemented for UserRepository")

    @repository_handler
    async def create(self, user_data: dict) -> UserRead | None:
        raise NotImplementedError("create() is not implemented for UserRepository")

    @repository_handler
    async def update(self, user_id: "BaseIdType", data: dict) -> UserRead | None:
        raise NotImplementedError("update() is not implemented for UserRepository")

    @repository_handler
    async def delete(self, user_id: "BaseIdType") -> bool:
        raise NotImplementedError("delete() is not implemented for UserRepository")
