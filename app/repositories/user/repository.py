import uuid
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import user_repo_logger
from app.models.postgre.user import User
from app.repositories.user.interface import IUserRepository
from app.schemas.user import UserInDB, UserCreate
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
    async def get_user_by_id(self, uid: uuid.UUID) -> Optional[UserInDB]:
        stmt = select(User).where(User.id == uid)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()

        return map_to_schema(db_user) if db_user else None

    @repository_handler
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()

        return map_to_schema(db_user) if db_user else None

    @repository_handler
    async def get_all_users(self) -> list[UserInDB]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        db_users = result.scalars().all()

        return [map_to_schema(user) for user in db_users]

    @repository_handler
    async def update_user(self, uid: uuid.UUID, user_update: Dict[str, Any]) -> Optional[UserInDB]:
        async with self._transaction():
            stmt = (
                update(User)
                .where(User.id == uid)
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
                update(User)
                .where(User.id == uid)
                .values(is_active=False)
            )
            result = await self.session.execute(stmt)

            return result.rowcount > 0

    @repository_handler
    async def hard_delete_user(self, uid: uuid.UUID) -> bool:
        async with self._transaction():
            stmt = (
                update(User)
                .where(User.id == uid)
            )
            result = await self.session.execute(stmt)

            return result.rowcount > 0

