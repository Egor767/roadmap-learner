from typing import TYPE_CHECKING

from sqlalchemy import select

from app.core.handlers import repository_handler
from app.models import User
from app.repositories import BaseRepository
from app.schemas.user import UserFilters
from app.schemas.user import UserRead

if TYPE_CHECKING:
    from app.core.types import BaseIdType


def map_to_schema(db_user: User | None) -> UserRead | None:
    if db_user:
        return UserRead.model_validate(db_user)
    return


class UserRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[UserRead] | list[None]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [map_to_schema(user) for user in users]

    @repository_handler
    async def get_by_filters(self, filters: UserFilters) -> list[UserRead] | list[None]:
        stmt = select(User)

        for field_name, value in vars(filters).items():
            if value is not None:
                column = getattr(User, field_name, None)
                if column is not None:
                    stmt = stmt.where(column == value)

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
