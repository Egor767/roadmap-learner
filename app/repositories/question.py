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
from app.core.enums import QuestionStatus
from app.core.handlers import repository_handler
from app.models import Module, Question, QuestionConcept, QuestionProgress, Roadmap
from app.repositories import BaseEntityRepository


class QuestionRepository(BaseEntityRepository):
    """Repository for question data access"""

    @repository_handler
    async def get_all(self, user: BaseIdType) -> list[Question]:
        stmt = (
            select(Question)
            .join(Module, Module.id == Question.module_id)
            .join(Roadmap, Roadmap.id == Module.roadmap_id)
            .where(Roadmap.user_id == user)
            .order_by(Question.question)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def get_by_id(self, id: BaseIdType, user: BaseIdType) -> Question:
        stmt = (
            select(Question)
            .join(Module, Module.id == Question.module_id)
            .join(Roadmap, Roadmap.id == Module.roadmap_id)
            .where(Roadmap.user_id == user, Question.id == id)
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Question, id)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Question]:
        stmt = (
            select(Question)
            .join(Module, Question.module_id == Module.id)
            .join(Roadmap, Module.roadmap_id == Roadmap.id)
            .where(Roadmap.user_id == user)
        )
        if status := filters.pop("status", None):
            stmt = stmt.join(
                QuestionProgress,
                and_(QuestionProgress.question_id == Question.id, QuestionProgress.user_id == user),
            ).where(QuestionProgress.status == status)
        if filters.get("roadmap_id"):
            stmt = stmt.where(Module.roadmap_id == filters.pop("roadmap_id"))
        for field_name, value in filters.items():
            column = getattr(Question, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        stmt = stmt.order_by(Question.question)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def get_status(self, id: BaseIdType, user: BaseIdType) -> QuestionStatus:
        """Return progress status for question and user"""
        stmt = select(QuestionProgress.status).where(
            QuestionProgress.user_id == user,
            QuestionProgress.question_id == id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or QuestionStatus.UNKNOWN

    @repository_handler
    async def get_statuses(
        self, user: BaseIdType, questions: list[BaseIdType]
    ) -> dict[BaseIdType, QuestionStatus]:
        stmt = (
            select(QuestionProgress.question_id, QuestionProgress.status)
            .join(Question, Question.id == QuestionProgress.question_id)
            .join(Module, Module.id == Question.module_id)
            .join(Roadmap, Roadmap.id == Module.roadmap_id)
            .where(
                QuestionProgress.user_id == user,
                QuestionProgress.question_id.in_(questions),
                Roadmap.user_id == user,
            )
        )
        result = await self.session.execute(stmt)
        found = {row.question_id: row.status for row in result.all()}
        return {qid: found.get(qid, QuestionStatus.UNKNOWN) for qid in questions}

    @repository_handler
    async def create(self, module: BaseIdType, data: dict, user: BaseIdType) -> Question:
        """Create and return new question verified against user through module"""
        async with transaction_manager(self.session):
            owned = (
                await self.session.execute(
                    select(Module.id)
                    .join(Roadmap, Roadmap.id == Module.roadmap_id)
                    .where(Module.id == module, Roadmap.user_id == user)
                )
            ).scalar_one_or_none()
            if owned is None:
                raise EntityNotFoundError(Module, module)
            data["module_id"] = module
            stmt = insert(Question).values(**data).returning(Question)
            return (await self.session.execute(stmt)).scalar_one()

    @repository_handler
    async def create_status(self, user: BaseIdType, id: BaseIdType) -> None:
        """Create initial status record for question and user"""
        async with transaction_manager(self.session):
            stmt = insert(QuestionProgress).values(
                user_id=user,
                question_id=id,
                status=QuestionStatus.UNKNOWN,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def update(self, id: BaseIdType, data: dict, user: BaseIdType) -> Question:
        """Update question by id verified against user and return updated entity"""
        async with transaction_manager(self.session):
            owned = (
                select(Module.id)
                .join(Roadmap, Roadmap.id == Module.roadmap_id)
                .where(Roadmap.user_id == user)
            )
            stmt = (
                update(Question)
                .where(Question.id == id, Question.module_id.in_(owned))
                .values(**data)
                .returning(Question)
            )
            row = (await self.session.execute(stmt)).scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Question, id)
            return row

    @repository_handler
    async def update_status(self, id: BaseIdType, status: QuestionStatus, user: BaseIdType) -> None:
        """Upsert progress status for question and user"""
        async with transaction_manager(self.session):
            owned = (
                await self.session.execute(
                    select(Question.id)
                    .join(Module, Module.id == Question.module_id)
                    .join(Roadmap, Roadmap.id == Module.roadmap_id)
                    .where(Question.id == id, Roadmap.user_id == user)
                )
            ).scalar_one_or_none()
            if owned is None:
                raise EntityNotFoundError(Question, id)
            stmt = (
                postgres_insert(QuestionProgress)
                .values(user_id=user, question_id=id, status=status)
                .on_conflict_do_update(
                    index_elements=["user_id", "question_id"],
                    set_={"status": status},
                )
            )
            await self.session.execute(stmt)

    @repository_handler
    async def delete(self, id: BaseIdType, user: BaseIdType) -> Question:
        """Delete question by id verified against user and return deleted entity"""
        async with transaction_manager(self.session):
            owned = (
                select(Module.id)
                .join(Roadmap, Roadmap.id == Module.roadmap_id)
                .where(Roadmap.user_id == user)
            )
            stmt = (
                delete(Question)
                .where(Question.id == id, Question.module_id.in_(owned))
                .returning(Question)
            )
            row = (await self.session.execute(stmt)).scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Question, id)
            return row

    @repository_handler
    async def create_multiple(
        self, user: BaseIdType, questions_by_module: dict[BaseIdType, list[dict]]
    ) -> list[Question]:
        """Create multiple questions across modules verified against user"""
        async with transaction_manager(self.session):
            module_ids = list(questions_by_module.keys())
            owned = (
                select(Module.id)
                .join(Roadmap, Roadmap.id == Module.roadmap_id)
                .where(Module.id.in_(module_ids), Roadmap.user_id == user)
            )
            result = await self.session.execute(owned)
            valid = {row for row in result.scalars().all()}
            invalid = set(module_ids) - valid
            if invalid:
                raise EntityNotFoundError(Module, next(iter(invalid)))
            all_questions = [q for questions in questions_by_module.values() for q in questions]
            result = await self.session.execute(
                insert(Question).values(all_questions).returning(Question)
            )
            return list(result.scalars().all())

    @repository_handler
    async def link_concept(self, id: BaseIdType, concept: BaseIdType, user: BaseIdType) -> None:
        """Link concept to question verified against user"""
        async with transaction_manager(self.session):
            owned = (
                await self.session.execute(
                    select(Question.id)
                    .join(Module, Module.id == Question.module_id)
                    .join(Roadmap, Roadmap.id == Module.roadmap_id)
                    .where(Question.id == id, Roadmap.user_id == user)
                )
            ).scalar_one_or_none()
            if owned is None:
                raise EntityNotFoundError(Question, id)
            await self.session.execute(
                insert(QuestionConcept).values(question_id=id, concept_id=concept)
            )

    @repository_handler
    async def unlink_concept(self, id: BaseIdType, concept: BaseIdType, user: BaseIdType) -> None:
        """Unlink concept from question verified against user"""
        async with transaction_manager(self.session):
            owned = (
                await self.session.execute(
                    select(Question.id)
                    .join(Module, Module.id == Question.module_id)
                    .join(Roadmap, Roadmap.id == Module.roadmap_id)
                    .where(Question.id == id, Roadmap.user_id == user)
                )
            ).scalar_one_or_none()
            if owned is None:
                raise EntityNotFoundError(Question, id)
            await self.session.execute(
                delete(QuestionConcept).where(
                    QuestionConcept.question_id == id,
                    QuestionConcept.concept_id == concept,
                )
            )
