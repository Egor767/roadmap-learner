from typing import List, Optional

from sqlalchemy import select, insert, update, delete, func

from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.core.types import BaseIdType
from app.models.session_manager import Session
from app.repositories import BaseRepository
from app.schemas.card import CardStatus
from app.schemas.session import (
    SessionInDB,
    SessionCreate,
    SessionFilters,
    SessionStatus,
    SubmitAnswerRequest,
)


def map_to_schema(db_session: Optional[Session]) -> Optional[SessionInDB]:
    if db_session:
        return SessionInDB.model_validate(db_session)
    return


class SessionManagerRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> List[SessionInDB]:
        stmt = select(Session)
        result = await self.session.execute(stmt)
        db_sessions = result.scalars().all()
        return [map_to_schema(session) for session in db_sessions]

    @repository_handler
    async def get_by_id(
        self,
        user_id: BaseIdType,
        session_id: BaseIdType,
    ) -> SessionInDB:
        stmt = select(Session).where(
            Session.id == session_id, Session.user_id == user_id
        )
        result = await self.session.execute(stmt)
        session = result.scalar_one_or_none()
        return map_to_schema(session)

    @repository_handler
    async def get_by_filters(
        self,
        user_id: BaseIdType,
        filters: SessionFilters,
    ) -> List[SessionInDB]:
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
    async def create(self, session_create_data: SessionCreate) -> SessionInDB:
        async with transaction_manager(self.session):
            stmt = insert(Session).values(**session_create_data).returning(Session)
            result = await self.session.execute(stmt)
            db_session = result.scalar_one_or_none()
            return map_to_schema(db_session)

    @repository_handler
    async def finish_session(
        self, user_id: BaseIdType, session_id: BaseIdType
    ) -> SessionInDB:
        async with transaction_manager(self.session):
            stmt = (
                update(Session)
                .where(
                    Session.id == session_id,
                    Session.user_id == user_id,
                    Session.status == SessionStatus.ACTIVE,
                )
                .values(status=SessionStatus.COMPLETED, completed_at=func.now())
                .returning(Session)
            )
            result = await self.session.execute(stmt)
            db_session = result.scalar_one_or_none()
            return map_to_schema(db_session)

    @repository_handler
    async def abandon_session(
        self, user_id: BaseIdType, session_id: BaseIdType
    ) -> bool:
        async with transaction_manager(self.session):
            stmt = (
                update(Session)
                .where(
                    Session.id == session_id,
                    Session.user_id == user_id,
                    Session.status == SessionStatus.ACTIVE,
                )
                .values(status=SessionStatus.ABANDONED, completed_at=func.now())
            )
            result = await self.session.execute(stmt)
            return result.rowcount > 0

    @repository_handler
    async def get_next_card_id(
        self, user_id: BaseIdType, session_id: BaseIdType
    ) -> Optional[BaseIdType]:
        stmt = select(Session).where(
            Session.id == session_id, Session.user_id == user_id
        )
        result = await self.session.execute(stmt)
        db_session = result.scalar_one_or_none()
        next_card_id = db_session.card_queue[db_session.current_card_index]
        if next_card_id:
            return next_card_id
        return

    @repository_handler
    async def submit_answer(
        self,
        user_id: BaseIdType,
        session_id: BaseIdType,
        answer_data: SubmitAnswerRequest,
    ) -> SessionInDB:
        async with transaction_manager(self.session):
            stmt = select(Session).where(
                Session.id == session_id, Session.user_id == user_id
            )
            result = await self.session.execute(stmt)
            db_session = result.scalar_one_or_none()

            update_data = {}

            if answer_data.answer == CardStatus.KNOWN:
                update_data["correct_answers"] = db_session.correct_answers + 1
            elif answer_data.answer == CardStatus.UNKNOWN:
                update_data["incorrect_answers"] = db_session.incorrect_answers + 1
            elif answer_data.answer == CardStatus.REVIEW:
                update_data["review_answers"] = db_session.review_answers + 1

            update_data["current_card_index"] = db_session.current_card_index + 1

            stmt = (
                update(Session)
                .where(Session.id == session_id, Session.user_id == user_id)
                .values(**update_data)
                .returning(Session)
            )

            result = await self.session.execute(stmt)
            updated_db_session = result.scalar_one_or_none()
            return map_to_schema(updated_db_session)

    @repository_handler
    async def delete(
        self,
        user_id: BaseIdType,
        session_id: BaseIdType,
    ) -> bool:
        async with transaction_manager(self.session):
            stmt = delete(Session).where(
                Session.id == session_id, Session.user_id == user_id
            )
            result = await self.session.execute(stmt)
            return result.rowcount > 0
