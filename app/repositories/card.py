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
from app.models import Card, Roadmap
from app.repositories import BaseRepository


class CardRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Card]:
        stmt = select(Card).order_by(Card.term)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, card: BaseIdType, user: BaseIdType) -> Card:
        stmt = select(Card).join(Roadmap, Card.roadmap_id == Roadmap.id).where(Card.id == card, Roadmap.user_id == user)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Card, card)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Card]:
        stmt = select(Card).join(Roadmap, Card.roadmap_id == Roadmap.id).where(Roadmap.user_id == user)
        for field_name, value in filters.items():
            column = getattr(Card, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        stmt = stmt.order_by(Card.term)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def create(self, data: dict, user: BaseIdType) -> Card:
        async with transaction_manager(self.session):
            roadmap_check_stmt = select(Roadmap.id).where(Roadmap.id == data.get("roadmap_id"), Roadmap.user_id == user)
            result = await self.session.execute(roadmap_check_stmt)
            if result.scalar_one_or_none() is None:
                raise EntityNotFoundError(Card, data.get("roadmap_id"))

            stmt = insert(Card).values(**data).returning(Card)
            result = await self.session.execute(stmt)
            row = result.scalar_one()
            return row

    @repository_handler
    async def update(self, card: BaseIdType, data: dict, user: BaseIdType) -> Card:
        async with transaction_manager(self.session):
            stmt = (
                update(Card)
                .where(
                    Card.id == card,
                    Card.roadmap_id.in_(select(Roadmap.id).where(Roadmap.user_id == user)),
                )
                .values(**data)
                .returning(Card)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Card, card)
            return row

    @repository_handler
    async def delete(self, card: BaseIdType, user: BaseIdType) -> Card:
        async with transaction_manager(self.session):
            stmt = (
                delete(Card)
                .where(
                    Card.id == card,
                    Card.roadmap_id.in_(select(Roadmap.id).where(Roadmap.user_id == user)),
                )
                .returning(Card)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Card, card)
            return row
