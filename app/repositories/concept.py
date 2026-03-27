from sqlalchemy import (
    and_,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as postgres_insert

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.enums import ConceptStatus
from app.core.handlers import repository_handler
from app.models import Concept, ConceptProgress, QuestionConcept, Roadmap
from app.repositories import BaseEntityRepository


class ConceptRepository(BaseEntityRepository):
    """Repository for concept data access"""

    @repository_handler
    async def get_all(self, user: BaseIdType) -> list[Concept]:
        """Return all concepts ordered by term"""
        stmt = (
            select(Concept)
            .join(Roadmap, Roadmap.id == Concept.roadmap_id)
            .where(Roadmap.user_id == user)
            .order_by(Concept.term)
        )
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, id: BaseIdType, user: BaseIdType) -> Concept:
        """Return concept by id"""
        stmt = (
            select(Concept)
            .join(Roadmap, Concept.roadmap_id == Roadmap.id)
            .where(Concept.id == id, Roadmap.user_id == user)
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Concept, id)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Concept]:
        """Return concepts matching filters for user"""
        stmt = (
            select(Concept)
            .join(Roadmap, Concept.roadmap_id == Roadmap.id)
            .where(Roadmap.user_id == user)
        )
        if question := filters.pop("question_id", None):
            stmt = stmt.join(QuestionConcept, Concept.id == QuestionConcept.concept_id).where(
                QuestionConcept.question_id == question
            )
        if status := filters.pop("status", None):
            stmt = stmt.join(
                ConceptProgress,
                and_(ConceptProgress.concept_id == Concept.id, ConceptProgress.user_id == user),
            ).where(ConceptProgress.status == status)
        for field, value in filters.items():
            column = getattr(Concept, field)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        stmt = stmt.order_by(Concept.term)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_question(self, question: BaseIdType, user: BaseIdType) -> list[Concept]:
        """Return concepts linked to question"""
        stmt = (
            select(Concept)
            .join(Roadmap, Concept.roadmap_id == Roadmap.id)
            .join(QuestionConcept, Concept.id == QuestionConcept.concept_id)
            .where(QuestionConcept.question_id == question, Roadmap.user_id == user)
            .order_by(Concept.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def get_status(self, id: BaseIdType, user: BaseIdType) -> ConceptStatus:
        """Return progress status for concept and user"""
        stmt = select(ConceptProgress.status).where(
            ConceptProgress.user_id == user, ConceptProgress.concept_id == id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or ConceptStatus.UNKNOWN

    @repository_handler
    async def get_statuses(
        self, user: BaseIdType, concepts: list[BaseIdType]
    ) -> dict[BaseIdType, ConceptStatus]:
        """Return progress statuses for multiple concepts"""
        stmt = select(ConceptProgress.concept_id, ConceptProgress.status).where(
            ConceptProgress.user_id == user,
            ConceptProgress.concept_id.in_(concepts),
        )
        result = await self.session.execute(stmt)
        found = {row.concept_id: row.status for row in result.all()}
        return {each: found.get(each, ConceptStatus.UNKNOWN) for each in concepts}

    @repository_handler
    async def create(self, data: dict) -> Concept:
        """Create and return new concept"""
        async with transaction_manager(self.session):
            roadmap_id = data["roadmap_id"]
            user_id = data.pop("user_id")
            owned = (
                await self.session.execute(
                    select(Roadmap.id).where(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
                )
            ).scalar_one_or_none()
            if owned is None:
                raise EntityNotFoundError(Roadmap, roadmap_id)
            stmt = insert(Concept).values(**data).returning(Concept)
            row = (await self.session.execute(stmt)).scalar_one()
            return row

    @repository_handler
    async def create_status(self, id: BaseIdType, user: BaseIdType) -> None:
        """Create initial status record for concept and user"""
        async with transaction_manager(self.session):
            stmt = insert(ConceptProgress).values(
                user_id=user,
                concept_id=id,
                status=ConceptStatus.UNKNOWN,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def update(self, id: BaseIdType, data: dict, user: BaseIdType) -> Concept:
        """Update concept by id and return updated entity"""
        async with transaction_manager(self.session):
            owned = select(Roadmap.id).where(Roadmap.user_id == user)
            stmt = (
                update(Concept)
                .where(Concept.id == id, Concept.roadmap_id.in_(owned))
                .values(**data)
                .returning(Concept)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Concept, id)
            return row

    @repository_handler
    async def update_status(self, id: BaseIdType, status: ConceptStatus, user: BaseIdType) -> None:
        """Upsert progress status for concept and user"""
        async with transaction_manager(self.session):
            owned = (
                await self.session.execute(
                    select(Concept.id)
                    .join(Roadmap, Concept.roadmap_id == Roadmap.id)
                    .where(Concept.id == id, Roadmap.user_id == user)
                )
            ).scalar_one_or_none()
            if owned is None:
                raise EntityNotFoundError(Concept, id)
            stmt = (
                postgres_insert(ConceptProgress)
                .values(user_id=user, concept_id=id, status=status)
                .on_conflict_do_update(
                    index_elements=["user_id", "concept_id"],
                    set_={"status": status},
                )
            )
            await self.session.execute(stmt)

    @repository_handler
    async def delete(self, id: BaseIdType, user: BaseIdType) -> Concept:
        """Delete concept by id verified against user and return deleted entity"""
        async with transaction_manager(self.session):
            owned = select(Roadmap.id).where(Roadmap.user_id == user)
            stmt = (
                delete(Concept)
                .where(Concept.id == id, Concept.roadmap_id.in_(owned))
                .returning(Concept)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Concept, id)
            return row
