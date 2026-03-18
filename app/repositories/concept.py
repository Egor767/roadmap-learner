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
from app.models import Concept, ConceptProgress, QuestionConcept, Roadmap
from app.repositories import BaseEntityRepository
from app.schemas.concept import ConceptStatus


class ConceptRepository(BaseEntityRepository):
    """Repository for concept data access."""

    @repository_handler
    async def get_all(self) -> list[Concept]:
        """Return all concepts ordered by term."""
        stmt = select(Concept).order_by(Concept.term)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, concept: BaseIdType) -> Concept:
        """Return concept by id."""
        stmt = select(Concept).where(Concept.id == concept)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Concept, concept)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Concept]:
        """Return concepts matching filters for user."""
        stmt = select(Concept).join(Roadmap, Concept.roadmap_id == Roadmap.id).where(Roadmap.user_id == user)
        for field_name, value in filters.items():
            column = getattr(Concept, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        stmt = stmt.order_by(Concept.term)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_question(self, question: BaseIdType) -> list[Concept]:
        """Return concepts linked to question."""
        stmt = (
            select(Concept)
            .join(QuestionConcept, Concept.id == QuestionConcept.concept_id)
            .where(QuestionConcept.question_id == question)
            .order_by(Concept.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def get_status(self, user: BaseIdType, concept: BaseIdType) -> ConceptStatus:
        """Return progress status for concept and user."""
        stmt = select(ConceptProgress.status).where(
            ConceptProgress.user_id == user,
            ConceptProgress.concept_id == concept,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or ConceptStatus.UNKNOWN

    @repository_handler
    async def get_statuses(self, user: BaseIdType, concepts: list[BaseIdType]) -> dict[BaseIdType, ConceptStatus]:
        """Return progress statuses for multiple concepts."""
        stmt = select(ConceptProgress.concept_id, ConceptProgress.status).where(
            ConceptProgress.user_id == user,
            ConceptProgress.concept_id.in_(concepts),
        )
        result = await self.session.execute(stmt)
        found = {row.concept_id: row.status for row in result.all()}
        return {cid: found.get(cid, ConceptStatus.UNKNOWN) for cid in concepts}

    @repository_handler
    async def get_ids_by_status(self, user: BaseIdType, status: ConceptStatus) -> list[BaseIdType]:
        """Return concept ids with given progress status for user."""
        stmt = select(ConceptProgress.concept_id).where(
            ConceptProgress.user_id == user,
            ConceptProgress.status == status,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def create(self, data: dict) -> Concept:
        """Create and return new concept."""
        async with transaction_manager(self.session):
            stmt = insert(Concept).values(**data).returning(Concept)
            result = await self.session.execute(stmt)
            row = result.scalar_one()
            return row

    @repository_handler
    async def create_progress(self, user: BaseIdType, concept: BaseIdType) -> None:
        """Create initial progress record for concept and user."""
        async with transaction_manager(self.session):
            stmt = insert(ConceptProgress).values(
                user_id=user,
                concept_id=concept,
                status=ConceptStatus.UNKNOWN,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def update(self, concept: BaseIdType, data: dict) -> Concept:
        """Update concept by id and return updated entity."""
        async with transaction_manager(self.session):
            stmt = update(Concept).where(Concept.id == concept).values(**data).returning(Concept)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Concept, concept)
            return row

    @repository_handler
    async def update_progress(self, user: BaseIdType, concept: BaseIdType, status: ConceptStatus) -> None:
        """Upsert progress status for concept and user."""
        async with transaction_manager(self.session):
            stmt = (
                insert(ConceptProgress)
                .values(user_id=user, concept_id=concept, status=status)
                .on_conflict_do_update(
                    index_elements=["user_id", "concept_id"],
                    set_={"status": status},
                )
            )
            await self.session.execute(stmt)

    @repository_handler
    async def delete(self, concept: BaseIdType) -> Concept:
        """Delete concept by id and return deleted entity."""
        async with transaction_manager(self.session):
            stmt = delete(Concept).where(Concept.id == concept).returning(Concept)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Concept, concept)
            return row
