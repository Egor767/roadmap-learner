from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.roadmap.repository import RoadMapRepository
from app.repositories.user.repository import UserRepository
from app.repositories.block.repository import BlockRepository
from app.repositories.card.repository import CardRepository

from app.services.roadmap.service import RoadMapService
from app.services.user.service import UserService
from app.services.block.service import BlockService
from app.services.card.service import CardService

from app.core.db import db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db.get_session():
        yield session


# user
async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


async def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    repo = UserRepository(session)
    return UserService(repo)


# roadmap
async def get_roadmap_repository(session: AsyncSession = Depends(get_db_session)) -> RoadMapRepository:
    return RoadMapRepository(session)


async def get_roadmap_service(session: AsyncSession = Depends(get_db_session)) -> RoadMapService:
    repo = RoadMapRepository(session)
    return RoadMapService(repo)


# block
async def get_block_repository(session: AsyncSession = Depends(get_db_session)) -> BlockRepository:
    return BlockRepository(session)


async def get_block_service(session: AsyncSession = Depends(get_db_session)) -> BlockService:
    repo = BlockRepository(session)
    return BlockService(repo)


# card
async def get_card_repository(session: AsyncSession = Depends(get_db_session)) -> CardRepository:
    return CardRepository(session)


async def get_card_service(session: AsyncSession = Depends(get_db_session)) -> CardService:
    repo = CardRepository(session)
    return CardService(repo)

