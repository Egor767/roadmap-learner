from sqlalchemy import (
    delete,
    func,
    insert,
    select,
    update,
)

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import Roadmap
from app.models.session import Session
from app.repositories import BaseRepository
from app.schemas.session import SessionStatus


class SessionRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Session]:
        stmt = select(Session)
        result = await self.session.execute(stmt)
        sessions = list(result.scalars().all())
        return sessions

    @repository_handler
    async def get_by_id(self, session_id: BaseIdType, user_id: BaseIdType) -> Session:
        stmt = select(Session).where(Session.id == session_id, Session.user_id == user_id)
        result = await self.session.execute(stmt)
        session = result.scalar_one_or_none()
        if session is None:
            raise EntityNotFoundError(Session, session_id)
        return session

    @repository_handler
    async def get_by_filters(self, filters: dict, user_id: BaseIdType) -> list[Session]:
        stmt = select(Session).where(Session.user_id == user_id)
        for field_name, value in filters.items():
            column = getattr(Roadmap, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        sessions = list(result.scalars().all())
        return sessions

    @repository_handler
    async def create(self, session_create_data: dict) -> Session:
        async with transaction_manager(self.session):
            stmt = insert(Session).values(**session_create_data).returning(Session)
            result = await self.session.execute(stmt)
            session = result.scalar_one()
            return session

    @repository_handler
    async def update(self, object_id: BaseIdType, update_data: dict, user_id: BaseIdType) -> Session:
        async with transaction_manager(self.session):
            stmt = (
                update(Session)
                .where(Session.id == object_id, Session.user_id == user_id)
                .values(**update_data)
                .returning(Session)
            )
            result = await self.session.execute(stmt)
            roadmap = result.scalar_one_or_none()
            if roadmap is None:
                raise EntityNotFoundError(Session, object_id)
            return roadmap

    @repository_handler
    async def finish_session(self, session_id: BaseIdType, user_id: BaseIdType) -> Session:
        async with transaction_manager(self.session):
            stmt = (
                update(Session)
                .where(
                    Session.id == session_id,
                    Session.status == SessionStatus.ACTIVE,
                    Session.user_id == user_id,
                )
                .values(status=SessionStatus.COMPLETED, completed_at=func.now())
                .returning(Session)
            )
            result = await self.session.execute(stmt)
            session = result.scalar_one_or_none()
            if session is None:
                raise EntityNotFoundError(Session, session_id)
            return session

    @repository_handler
    async def abandon_session(self, session_id: BaseIdType, user_id: BaseIdType):
        async with transaction_manager(self.session):
            stmt = (
                update(Session)
                .where(
                    Session.id == session_id,
                    Session.status == SessionStatus.ACTIVE,
                    Session.user_id == user_id,
                )
                .values(status=SessionStatus.ABANDONED, completed_at=func.now())
            )
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Session, session_id)

    @repository_handler
    async def delete(self, session_id: BaseIdType):
        async with transaction_manager(self.session):
            stmt = delete(Session).where(Session.id == session_id)
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Session, session_id)
