from typing import List, Optional

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import transaction_manager
from app.core.handlers import repository_handler
from app.core.types import BaseIDType
from app.models.postgres.user import User
from app.schemas.user import UserInDB, UserFilters


def map_to_schema(db_user: Optional[User]) -> Optional[UserInDB]:
    if db_user:
        return UserInDB.model_validate(db_user)
    return


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @repository_handler
    async def get_all_users(self) -> List[UserInDB]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [map_to_schema(user) for user in users]

    @repository_handler
    async def get_user_by_id(self, uid: BaseIDType) -> Optional[UserInDB]:
        stmt = select(User).where(User.id == uid)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user:
            return UserInDB.from_orm(db_user)
        return

    @repository_handler
    async def get_users(self, filters: UserFilters) -> List[UserInDB]:
        stmt = select(User)

        if filters.email:
            stmt = stmt.where(User.email == filters.email)
        if filters.username:
            stmt = stmt.where(User.username == filters.username)

        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [map_to_schema(user) for user in users]

    @repository_handler
    async def create_user(self, user_data: dict) -> UserInDB:
        async with transaction_manager(self.session):
            stmt = insert(User).values(**user_data).returning(User)
            result = await self.session.execute(stmt)
            db_user = result.scalar_one_or_none()
            return map_to_schema(db_user)

    @repository_handler
    async def delete_user(self, uid: BaseIDType) -> bool:
        async with transaction_manager(self.session):
            stmt = delete(User).where(User.id == uid)
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def update_user(self, uid: BaseIDType, user_data: dict) -> UserInDB:
        async with transaction_manager(self.session):
            stmt = (
                update(User).where(User.id == uid).values(**user_data).returning(User)
            )
            result = await self.session.execute(stmt)
            db_user = result.scalar_one_or_none()
            return map_to_schema(db_user)
