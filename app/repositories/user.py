from typing import List, Optional

from sqlalchemy import select

from core.handlers import repository_handler
from models import User
from repositories import BaseRepository
from schemas.user import UserFilters
from schemas.user import UserRead


def map_to_schema(db_user: Optional[User]) -> Optional[UserRead]:
    if db_user:
        return UserRead.model_validate(db_user)
    return


class UserRepository(BaseRepository):
    @repository_handler
    async def get_all_users(self) -> List[UserRead]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [map_to_schema(user) for user in users]

    @repository_handler
    async def get_users(self, filters: UserFilters) -> List[UserRead]:
        stmt = select(User)

        if filters.email is not None:
            stmt = stmt.where(User.email == filters.email)
        if filters.username is not None:
            stmt = stmt.where(User.username == filters.username)

        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [map_to_schema(user) for user in users]
