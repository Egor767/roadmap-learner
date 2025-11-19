from typing import Annotated, TYPE_CHECKING
from fastapi import Depends

from .db import get_db_session
from repositories import CardRepository
from services import CardService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_card_repository(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_session),
    ],
) -> CardRepository:
    yield CardRepository(session)


async def get_card_service(
    repo: Annotated[
        CardRepository,
        Depends(get_card_repository),
    ],
) -> CardService:
    yield CardService(repo)
