import uuid
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import user_repo_logger
from app.models.postgres.user import User
from app.repositories.user.interface import IUserRepository
from app.schemas.user import UserInDB, UserCreate, UserFilters
from app.core.handlers import repository_handler


def map_to_schema(db_user: User) -> UserInDB:
    return UserInDB.model_validate(db_user)


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def _transaction(self):
        try:
            yield
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    @repository_handler
    async def create_user(self, user: UserCreate) -> UserInDB:
        async with self._transaction():
            user_data = user.model_dump(exclude={'password'})
            user_data['hashed_password'] = user.password
            stmt = insert(User).values(**user_data).returning(User)
            result = await self.session.execute(stmt)
            db_user = result.scalar_one()

            return map_to_schema(db_user)

    @repository_handler
    async def get_all_users(self) -> Optional[List[UserInDB]]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        users = result.scalars().all()

        if not users:
            return
        return [map_to_schema(user) for user in users]

    @repository_handler
    async def get_user_by_id(self, uid: uuid.UUID) -> Optional[UserInDB]:
        stmt = select(User).where(User.user_id == uid)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if not db_user:
            return
        return map_to_schema(db_user)

    async def get_users_by_filters(self, filters: UserFilters) -> Optional[List[UserInDB]]:
        stmt = select(User)

        if filters.email:
            stmt = stmt.where(User.email == filters.email)
        if filters.username:
            stmt = stmt.where(User.username == filters.username)

        result = await self.session.execute(stmt)
        users = result.scalars().all()

        if not users:
            return
        return [map_to_schema(user) for user in users]

    @repository_handler
    async def update_user(self, uid: uuid.UUID, user_update: Dict[str, Any]) -> Optional[UserInDB]:
        async with self._transaction():
            stmt = (
                update(User)
                .where(User.user_id == uid)
                .values(**user_update)
                .returning(User)
            )
            result = await self.session.execute(stmt)
            db_user = result.scalar_one_or_none()

            return map_to_schema(db_user) if db_user else None

    @repository_handler
    async def delete_user(self, uid: uuid.UUID) -> bool:
        async with self._transaction():
            stmt = (
                delete(User)
                .where(User.user_id == uid)
            )
            result = await self.session.execute(stmt)

            return result.rowcount > 0

    @repository_handler
    async def hard_delete_user(self, uid: uuid.UUID) -> bool:
        async with self._transaction():
            stmt = (
                update(User)
                .where(User.user_id == uid)
            )
            result = await self.session.execute(stmt)

            return result.rowcount > 0

