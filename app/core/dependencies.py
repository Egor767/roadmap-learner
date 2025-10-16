from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user.repository import UserRepository
from app.services.user.service import UserService
from app.core.db import db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db.get_session():
        yield session


async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


async def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


