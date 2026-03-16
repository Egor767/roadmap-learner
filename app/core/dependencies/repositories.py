from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.repositories import (
    BlockRepository,
    CardRepository,
    QuestionRepository,
    RoadmapRepository,
    SessionRepository,
    UserRepository,
    VerifyRepository,
)

from .db import get_db_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def get_verify_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> VerifyRepository:
    return VerifyRepository(session)


def get_user_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> UserRepository:
    return UserRepository(session)


def get_roadmap_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> RoadmapRepository:
    return RoadmapRepository(session)


def get_block_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> BlockRepository:
    return BlockRepository(session)


def get_card_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> CardRepository:
    return CardRepository(session)


def get_question_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> QuestionRepository:
    return QuestionRepository(session)


def get_session_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> SessionRepository:
    return SessionRepository(session)
