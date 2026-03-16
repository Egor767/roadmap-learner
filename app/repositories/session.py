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
from app.models import Session
from app.repositories import BaseEntityRepository
from app.schemas.session import SessionStatus


class SessionRepository(BaseEntityRepository):
    @repository_handler
    async def get_all(self) -> list[Session]:
        stmt = select(Session).order_by(Session.updated_at)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, session: BaseIdType, user: BaseIdType) -> Session:
        stmt = select(Session).where(Session.id == session, Session.user_id == user)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Session, session)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Session]:
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
    async def get_questions(self, session: BaseIdType, user: BaseIdType) -> list[BaseIdType]:
        stmt = select(Session.questions).where(Session.id == session, Session.user_id == user)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Session, session)
        return row or []

    @repository_handler
    async def create(self, data: dict) -> Session:
        async with transaction_manager(self.session):
            stmt = insert(Session).values(**data).returning(Session)
            result = await self.session.execute(stmt)
            row = result.scalar_one()
            return row

    @repository_handler
    async def update(self, session: BaseIdType, data: dict, user: BaseIdType) -> Session:
        async with transaction_manager(self.session):
            stmt = (
                update(Session).where(Session.id == session, Session.user_id == user).values(**data).returning(Session)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Session, session)
            return row

    @repository_handler
    async def finish_session(self, session: BaseIdType, user: BaseIdType) -> Session:
        async with transaction_manager(self.session):
            stmt = (
                update(Session)
                .where(
                    Session.id == session,
                    Session.status == SessionStatus.ACTIVE,
                    Session.user_id == user,
                )
                .values(status=SessionStatus.COMPLETED, completed_at=func.now())
                .returning(Session)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Session, session)
            return row

    @repository_handler
    async def abandon_session(self, session: BaseIdType, user: BaseIdType):
        async with transaction_manager(self.session):
            stmt = (
                update(Session)
                .where(
                    Session.id == session,
                    Session.status == SessionStatus.ACTIVE,
                    Session.user_id == user,
                )
                .values(status=SessionStatus.ABANDONED, completed_at=func.now())
            )
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Session, session)

    @repository_handler
    async def delete(self, session: BaseIdType):
        async with transaction_manager(self.session):
            stmt = delete(Session).where(Session.id == session)
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                raise EntityNotFoundError(Session, session)
