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
from app.models import Session, SessionItem
from app.repositories import BaseEntityRepository
from app.schemas.session import SessionStatus


class SessionRepository(BaseEntityRepository):
    """Repository for session data access."""

    @repository_handler
    async def get_all(self) -> list[Session]:
        """Return all sessions ordered by update time."""
        stmt = select(Session).order_by(Session.updated_at)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, session: BaseIdType) -> Session:
        """Return session by id."""
        stmt = select(Session).where(Session.id == session)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Session, session)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Session]:
        """Return sessions matching filters for user."""
        stmt = select(Session).where(Session.user_id == user)
        for field_name, value in filters.items():
            column = getattr(Session, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        stmt = stmt.order_by(Session.updated_at)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_questions(self, session: BaseIdType) -> list[BaseIdType]:
        """Return ordered question ids for session."""
        stmt = select(Session.questions).where(Session.id == session)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Session, session)
        return row or []

    @repository_handler
    async def get_item_by_id(self, item: BaseIdType) -> SessionItem:
        """Return session item by id."""
        stmt = select(SessionItem).where(SessionItem.id == item)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(SessionItem, item)
        return row

    @repository_handler
    async def get_items_by_session(self, session: BaseIdType) -> list[SessionItem]:
        """Return all items for session."""
        stmt = select(SessionItem).where(SessionItem.session_id == session)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def get_answered_ids(self, session: BaseIdType) -> set[BaseIdType]:
        """Return ids of already answered questions in session."""
        stmt = select(SessionItem.question_id).where(SessionItem.session_id == session)
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    @repository_handler
    async def create(self, data: dict) -> Session:
        """Create and return new session."""
        async with transaction_manager(self.session):
            stmt = insert(Session).values(**data).returning(Session)
            result = await self.session.execute(stmt)
            row = result.scalar_one()
            return row

    @repository_handler
    async def create_item(self, data: dict) -> SessionItem:
        """Create and return new session item."""
        async with transaction_manager(self.session):
            stmt = insert(SessionItem).values(**data).returning(SessionItem)
            result = await self.session.execute(stmt)
            return result.scalar_one()

    @repository_handler
    async def update(self, session: BaseIdType, data: dict) -> Session:
        """Update session by id and return updated entity."""
        async with transaction_manager(self.session):
            stmt = update(Session).where(Session.id == session).values(**data).returning(Session)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Session, session)
            return row

    @repository_handler
    async def update_item(self, item: BaseIdType, data: dict) -> SessionItem:
        """Update session item by id and return updated entity."""
        async with transaction_manager(self.session):
            stmt = update(SessionItem).where(SessionItem.id == item).values(**data).returning(SessionItem)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(SessionItem, item)
            return row

    @repository_handler
    async def finish_session(self, session: BaseIdType) -> Session:
        """Mark session as completed and return updated entity."""
        async with transaction_manager(self.session):
            stmt = (
                update(Session)
                .where(Session.id == session, Session.status == SessionStatus.ACTIVE)
                .values(status=SessionStatus.COMPLETED, completed_at=func.now())
                .returning(Session)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Session, session)
            return row

    @repository_handler
    async def abandon_session(self, session: BaseIdType) -> None:
        """Mark session as abandoned."""
        async with transaction_manager(self.session):
            stmt = (
                update(Session)
                .where(Session.id == session, Session.status == SessionStatus.ACTIVE)
                .values(status=SessionStatus.ABANDONED, completed_at=func.now())
            )
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Session, session)

    @repository_handler
    async def delete(self, session: BaseIdType) -> None:
        """Delete session by id."""
        async with transaction_manager(self.session):
            stmt = delete(Session).where(Session.id == session)
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Session, session)
