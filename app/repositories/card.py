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
from app.models import Card, CardProgress, QuestionCard, Roadmap
from app.models.card_progress import CardStatus
from app.repositories import BaseEntityRepository


class CardRepository(BaseEntityRepository):
    """Repository for card data access."""

    @repository_handler
    async def get_all(self) -> list[Card]:
        """Return all cards ordered by term."""
        stmt = select(Card).order_by(Card.term)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, card: BaseIdType) -> Card:
        """Return card by id."""
        stmt = select(Card).where(Card.id == card)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Card, card)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Card]:
        """Return cards matching filters for user."""
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
    async def get_by_question(self, question: BaseIdType) -> list[Card]:
        """Return cards linked to question."""
        stmt = (
            select(Card)
            .join(QuestionCard, Card.id == QuestionCard.card_id)
            .where(QuestionCard.question_id == question)
            .order_by(Card.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def get_status(self, user: BaseIdType, card: BaseIdType) -> CardStatus:
        """Return progress status for card and user."""
        stmt = select(CardProgress.status).where(
            CardProgress.user_id == user,
            CardProgress.card_id == card,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or CardStatus.UNKNOWN

    @repository_handler
    async def get_statuses(self, user: BaseIdType, cards: list[BaseIdType]) -> dict[BaseIdType, CardStatus]:
        """Return progress statuses for multiple cards."""
        stmt = select(CardProgress.card_id, CardProgress.status).where(
            CardProgress.user_id == user,
            CardProgress.card_id.in_(cards),
        )
        result = await self.session.execute(stmt)
        found = {row.card_id: row.status for row in result.all()}
        return {cid: found.get(cid, CardStatus.UNKNOWN) for cid in cards}

    @repository_handler
    async def get_ids_by_status(self, user: BaseIdType, status: CardStatus) -> list[BaseIdType]:
        """Return card ids with given progress status for user."""
        stmt = select(CardProgress.card_id).where(
            CardProgress.user_id == user,
            CardProgress.status == status,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def create(self, data: dict) -> Card:
        """Create and return new card."""
        async with transaction_manager(self.session):
            stmt = insert(Card).values(**data).returning(Card)
            result = await self.session.execute(stmt)
            row = result.scalar_one()
            return row

    @repository_handler
    async def create_progress(self, user: BaseIdType, card: BaseIdType) -> None:
        """Create initial progress record for card and user."""
        async with transaction_manager(self.session):
            stmt = insert(CardProgress).values(
                user_id=user,
                card_id=card,
                status=CardStatus.UNKNOWN,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def update(self, card: BaseIdType, data: dict) -> Card:
        """Update card by id and return updated entity."""
        async with transaction_manager(self.session):
            stmt = update(Card).where(Card.id == card).values(**data).returning(Card)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Card, card)
            return row

    @repository_handler
    async def update_progress(self, user: BaseIdType, card: BaseIdType, status: CardStatus) -> None:
        """Upsert progress status for card and user."""
        async with transaction_manager(self.session):
            stmt = (
                insert(CardProgress)
                .values(user_id=user, card_id=card, status=status)
                .on_conflict_do_update(
                    index_elements=["user_id", "card_id"],
                    set_={"status": status},
                )
            )
            await self.session.execute(stmt)

    @repository_handler
    async def delete(self, card: BaseIdType) -> Card:
        """Delete card by id and return deleted entity."""
        async with transaction_manager(self.session):
            stmt = delete(Card).where(Card.id == card).returning(Card)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Card, card)
            return row
