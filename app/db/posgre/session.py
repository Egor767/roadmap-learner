from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.db.interface import ISession
from app.core.config import db_config

Base = declarative_base()


class PosgreAsyncSession(ISession):
    def __init__(self):
        self.engine = None
        self.async_session_local = None

    async def create_engine(self):
        self.engine = create_async_engine(
            db_config.url,
            echo=True,
            future=True,
            poolclass=NullPool
        )
        self.async_session_local = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self):
        async with self.async_session_local() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

