from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.postgres.db_helper import db_helper


@asynccontextmanager
async def transaction_manager(session: AsyncSession):
    try:
        yield
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.session_dependency():
        yield session
