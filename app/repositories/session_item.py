from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import SessionItem


class SessionItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @repository_handler
    async def get_by_id(self, item: BaseIdType) -> SessionItem:
        stmt = select(SessionItem).where(SessionItem.id == item)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(SessionItem, item)
        return row

    @repository_handler
    async def get_by_session(self, session: BaseIdType) -> list[SessionItem]:
        stmt = select(SessionItem).where(SessionItem.session_id == session)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def get_answered_ids(self, session: BaseIdType) -> set[BaseIdType]:
        stmt = select(SessionItem.question_id).where(
            SessionItem.session_id == session,
        )
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    @repository_handler
    async def create(self, data: dict) -> SessionItem:
        async with transaction_manager(self.session):
            stmt = insert(SessionItem).values(**data).returning(SessionItem)
            result = await self.session.execute(stmt)
            return result.scalar_one()

    @repository_handler
    async def update(self, item: BaseIdType, data: dict) -> SessionItem:
        async with transaction_manager(self.session):
            stmt = update(SessionItem).where(SessionItem.id == item).values(**data).returning(SessionItem)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(SessionItem, item)
            return row
