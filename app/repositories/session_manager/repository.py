import uuid
from contextlib import asynccontextmanager
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.core.logging import session_manager_repository_logger as logger
from app.core.handlers import repository_handler
from app.models.postgres.session_manager import Session
from app.repositories.session_manager.interface import ISessionManagerRepository
from app.schemas.card import CardStatus, CardInDB
from app.schemas.session_manager import SessionInDB, SessionCreate, SessionFilters, SessionResult


def map_to_schema(db_session: Session) -> SessionInDB:
    return SessionInDB.model_validate(db_session)


class SessionManagerRepository(ISessionManagerRepository):
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
    async def get_all_sessions(self) -> List[SessionInDB]:
        stmt = select(Session)
        result = await self.session.execute(stmt)
        db_sessions = result.scalars().all()
        return [map_to_schema(session) for session in db_sessions]

    @repository_handler
    async def get_user_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> SessionInDB:
        stmt = select(Session).where(
            Session.session_id == session_id,
            Session.user_id == user_id
        )
        result = await self.session.execute(stmt)
        session = result.scalar_one_or_none()
        logger.info(f"session: {session}, schema: {map_to_schema(session)}")
        return map_to_schema(session) if session else None

    @repository_handler
    async def get_user_sessions(self, user_id: uuid.UUID, filters: SessionFilters) -> List[SessionInDB]:
        stmt = select(Session).where(Session.user_id == user_id)

        if filters.roadmap_id:
            stmt = stmt.where(Session.roadmap_id == filters.roadmap_id)
        if filters.block_id:
            stmt = stmt.where(Session.block_id == filters.block_id)
        if filters.mode:
            stmt = stmt.where(Session.mode == filters.mode)
        if filters.status:
            stmt = stmt.where(Session.status == filters.status)

        result = await self.session.execute(stmt)
        db_sessions = result.scalars().all()
        return [map_to_schema(session) for session in db_sessions]

    @repository_handler
    async def create_session(self, session_create_data: SessionCreate) -> SessionInDB:
        async with self._transaction():
            stmt = insert(Session).values(**session_create_data).returning(Session)
            result = await self.session.execute(stmt)
            db_session = result.scalar_one()
            return map_to_schema(db_session)

    @repository_handler
    async def finish_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> SessionResult:
        ...

    @repository_handler
    async def abandon_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> bool:
        ...

    @repository_handler
    async def get_next_card(self, user_id: uuid.UUID, session_id: uuid.UUID, limit: int) -> CardInDB:
        ...

    @repository_handler
    async def submit_answer(self, user_id: uuid.UUID, session_id: uuid.UUID, card_id: uuid.UUID, answer: CardStatus) -> SessionInDB:
        ...

