from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.roadmap import RoadmapRepository
from app.repositories.user import UserRepository
from app.repositories.block import BlockRepository
from app.repositories.card import CardRepository
from app.repositories.session_manager import SessionManagerRepository

from app.services.roadmap import RoadMapService
from app.services.user import UserService
from app.services.block import BlockService
from app.services.card import CardService
from app.services.session_manager import SessionManagerService

from app.models.postgres.db_helper import db_helper


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


# user
async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(session)


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


# roadmap
async def get_roadmap_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RoadmapRepository:
    return RoadmapRepository(session)


async def get_roadmap_service(
    session: AsyncSession = Depends(get_db_session),
) -> RoadMapService:
    repo = RoadmapRepository(session)
    return RoadMapService(repo)


# block
async def get_block_repository(
    session: AsyncSession = Depends(get_db_session),
) -> BlockRepository:
    return BlockRepository(session)


async def get_block_service(
    session: AsyncSession = Depends(get_db_session),
) -> BlockService:
    repo = BlockRepository(session)
    return BlockService(repo)


# card
async def get_card_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CardRepository:
    return CardRepository(session)


async def get_card_service(
    session: AsyncSession = Depends(get_db_session),
) -> CardService:
    repo = CardRepository(session)
    return CardService(repo)


# session manager
async def get_session_manager_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SessionManagerRepository:
    return SessionManagerRepository(session)


async def get_session_manager_service(
    session: AsyncSession = Depends(get_db_session),
) -> SessionManagerService:
    repo = SessionManagerRepository(session)
    return SessionManagerService(repo)
