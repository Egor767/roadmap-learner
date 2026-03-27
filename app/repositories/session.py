from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import Roadmap, Session, SessionItem
from app.repositories import BaseEntityRepository


class SessionRepository(BaseEntityRepository):
    """Repository for session data access"""

    @repository_handler
    async def get_all(self, user: BaseIdType) -> list[Session]:
        """Return all sessions ordered by update time"""
        stmt = select(Session).where(Session.user_id == user).order_by(Session.updated_at)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, id: BaseIdType, user: BaseIdType) -> Session:
        """Return session by id"""
        stmt = select(Session).where(Session.id == id, Session.user_id == user)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Session, id)
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
    async def get_questions(self, id: BaseIdType, user: BaseIdType) -> list[BaseIdType]:
        """Return ordered question ids for session."""
        stmt = select(Session.questions).where(Session.id == id, Session.user_id == user)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Session, id)
        return row or []

    @repository_handler
    async def get_item_by_id(self, id: BaseIdType) -> SessionItem:
        """Return session item by id."""
        stmt = select(SessionItem).where(SessionItem.id == id)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(SessionItem, id)
        return row

    @repository_handler
    async def get_items_by_session(self, id: BaseIdType, user: BaseIdType) -> list[SessionItem]:
        """Return all items for session."""
        stmt = (
            select(SessionItem)
            .join(Session, Session.id == SessionItem.session_id)
            .where(SessionItem.session_id == id, Session.user_id == user)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def get_answered_ids(self, id: BaseIdType, user: BaseIdType) -> set[BaseIdType]:
        """Return ids of already answered questions in session."""
        stmt = (
            select(SessionItem.question_id)
            .join(Session, Session.id == SessionItem.session_id)
            .where(SessionItem.session_id == id, Session.user_id == user)
        )
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def _verify_ownership(self, roadmap: BaseIdType, user: BaseIdType) -> None:
        """Raise if roadmap does not belong to user"""
        stmt = select(Roadmap.id).where(Roadmap.id == roadmap, Roadmap.user_id == user)
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        if result is None:
            raise EntityNotFoundError(Roadmap, roadmap)

    @repository_handler
    async def create(self, data: dict) -> Session:
        """Create and return new session."""
        async with transaction_manager(self.session):
            await self._verify_ownership(data.get("roadmap_id"), data.get("user_id"))
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
    async def update(self, session: BaseIdType, data: dict, user: BaseIdType) -> Session:
        """Update session by id and return updated entity."""
        async with transaction_manager(self.session):
            owned = select(Roadmap.id).where(Roadmap.user_id == user)
            stmt = (
                update(Session)
                .where(Session.id == session, Session.roadmap_id.in_(owned))
                .values(**data)
                .returning(Session)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Session, session)
            return row

    @repository_handler
    async def update_item(self, item: BaseIdType, data: dict) -> SessionItem:
        """Update session item by id and return updated entity."""
        async with transaction_manager(self.session):
            stmt = (
                update(SessionItem)
                .where(SessionItem.id == item)
                .values(**data)
                .returning(SessionItem)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(SessionItem, item)
            return row

    @repository_handler
    async def delete(self, id: BaseIdType, user: BaseIdType) -> None:
        """Delete session by id."""
        async with transaction_manager(self.session):
            stmt = delete(Session).where(Session.id == id, Session.user_id == user)
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Session, id)
