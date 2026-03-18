from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.repositories import (
    ConceptRepository,
    ModuleRepository,
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


def get_module_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> ModuleRepository:
    return ModuleRepository(session)


def get_concept_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> ConceptRepository:
    return ConceptRepository(session)


def get_question_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> QuestionRepository:
    return QuestionRepository(session)


def get_session_repository(
    session: Annotated["AsyncSession", Depends(get_db_session)],
) -> SessionRepository:
    return SessionRepository(session)
