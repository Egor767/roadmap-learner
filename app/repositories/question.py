from typing import Literal

from sqlalchemy import (
    delete,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as postgres_insert

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.dependencies import transaction_manager
from app.core.handlers import repository_handler
from app.models import Module, Question, QuestionConcept, QuestionProgress, Roadmap
from app.models.question_progress import QuestionStatus
from app.repositories import BaseEntityRepository


class QuestionRepository(BaseEntityRepository):
    """Repository for question data access."""

    @repository_handler
    async def get_all(self) -> list[Question]:
        """Return all questions ordered by index."""
        stmt = select(Question).order_by(Question.order_index)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, question: BaseIdType) -> Question:
        """Return question by id."""
        stmt = select(Question).where(Question.id == question)
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Question, question)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Question]:
        """Return questions matching filters for user."""
        stmt = (
            select(Question)
            .join(Module, Question.module_id == Module.id)
            .join(Roadmap, Module.roadmap_id == Roadmap.id)
            .where(Roadmap.user_id == user)
        )
        if filters.get("roadmap_id") is not None:
            stmt = stmt.where(Module.roadmap_id == filters.pop("roadmap_id"))
        for field_name, value in filters.items():
            column = getattr(Question, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        stmt = stmt.order_by(Question.order_index)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_status(self, user: BaseIdType, question: BaseIdType) -> QuestionStatus:
        """Return progress status for question and user."""
        stmt = select(QuestionProgress.status).where(
            QuestionProgress.user_id == user,
            QuestionProgress.question_id == question,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() or QuestionStatus.UNKNOWN

    @repository_handler
    async def get_statuses(self, user: BaseIdType, questions: list[BaseIdType]) -> dict[BaseIdType, QuestionStatus]:
        """Return progress statuses for multiple questions."""
        stmt = select(QuestionProgress.question_id, QuestionProgress.status).where(
            QuestionProgress.user_id == user,
            QuestionProgress.question_id.in_(questions),
        )
        result = await self.session.execute(stmt)
        found = {row.question_id: row.status for row in result.all()}
        return {qid: found.get(qid, QuestionStatus.UNKNOWN) for qid in questions}

    @repository_handler
    async def get_ids_by_status(self, user: BaseIdType, status: QuestionStatus) -> list[BaseIdType]:
        """Return question ids with given progress status for user."""
        stmt = select(QuestionProgress.question_id).where(
            QuestionProgress.user_id == user,
            QuestionProgress.status == status,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @repository_handler
    async def create(
        self,
        module_id: BaseIdType,
        data: dict,
        position: Literal["start", "end"] = "end",
        previous: BaseIdType | None = None,
    ) -> Question:
        """Create question in module at given position."""
        async with transaction_manager(self.session):
            if previous is not None:
                prev_stmt = select(Question.order_index).where(
                    Question.id == previous,
                    Question.module_id == module_id,
                )
                prev_index = (await self.session.execute(prev_stmt)).scalar_one_or_none()
                if prev_index is None:
                    raise EntityNotFoundError(Question, previous)
                await self.session.execute(
                    update(Question)
                    .where(Question.module_id == module_id, Question.order_index > prev_index)
                    .values(order_index=Question.order_index + 1)
                )
                data["order_index"] = prev_index + 1
            elif position == "start":
                await self.session.execute(
                    update(Question).where(Question.module_id == module_id).values(order_index=Question.order_index + 1)
                )
                data["order_index"] = 0
            else:
                max_stmt = select(func.max(Question.order_index)).where(Question.module_id == module_id)
                max_index = (await self.session.execute(max_stmt)).scalar()
                data["order_index"] = (max_index + 1) if max_index is not None else 0
            stmt = insert(Question).values(**data).returning(Question)
            return (await self.session.execute(stmt)).scalar_one()

    @repository_handler
    async def create_progress(self, user: BaseIdType, question: BaseIdType) -> None:
        """Create initial progress record for question and user."""
        async with transaction_manager(self.session):
            stmt = insert(QuestionProgress).values(
                user_id=user,
                question_id=question,
                status=QuestionStatus.UNKNOWN,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def move(
        self,
        module_id: BaseIdType,
        question_id: BaseIdType,
        previous: BaseIdType | None,
    ) -> tuple[Question, list[BaseIdType]]:
        """Move question to new position within module."""
        async with transaction_manager(self.session):
            stmt = select(Question).where(
                Question.id == question_id,
                Question.module_id == module_id,
            )
            row = (await self.session.execute(stmt)).scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Question, question_id)
            old_index = row.order_index
            if previous is None:
                new_index = 0
            else:
                prev_stmt = select(Question.order_index).where(
                    Question.id == previous,
                    Question.module_id == module_id,
                )
                after_index = (await self.session.execute(prev_stmt)).scalar_one_or_none()
                if after_index is None:
                    raise EntityNotFoundError(Question, previous)
                new_index = after_index + 1 if after_index < old_index else after_index
            if new_index == old_index:
                return row, []
            if new_index < old_index:
                affected_stmt = select(Question.id).where(
                    Question.module_id == module_id,
                    Question.order_index >= new_index,
                    Question.order_index < old_index,
                    Question.id != question_id,
                )
                await self.session.execute(
                    update(Question)
                    .where(
                        Question.module_id == module_id,
                        Question.order_index >= new_index,
                        Question.order_index < old_index,
                        Question.id != question_id,
                    )
                    .values(order_index=Question.order_index + 1)
                )
            else:
                affected_stmt = select(Question.id).where(
                    Question.module_id == module_id,
                    Question.order_index > old_index,
                    Question.order_index <= new_index,
                    Question.id != question_id,
                )
                await self.session.execute(
                    update(Question)
                    .where(
                        Question.module_id == module_id,
                        Question.order_index > old_index,
                        Question.order_index <= new_index,
                        Question.id != question_id,
                    )
                    .values(order_index=Question.order_index - 1)
                )
            affected_ids = (await self.session.execute(affected_stmt)).scalars().all()
            result = await self.session.execute(
                update(Question).where(Question.id == question_id).values(order_index=new_index).returning(Question)
            )
            return result.scalar_one(), list(affected_ids)

    @repository_handler
    async def update(self, question: BaseIdType, data: dict) -> Question:
        """Update question by id and return updated entity."""
        async with transaction_manager(self.session):
            stmt = update(Question).where(Question.id == question).values(**data).returning(Question)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Question, question)
            return row

    @repository_handler
    async def update_progress(self, user: BaseIdType, question: BaseIdType, status: QuestionStatus) -> None:
        """Upsert progress status for question and user."""
        async with transaction_manager(self.session):
            stmt = (
                postgres_insert(QuestionProgress)
                .values(user_id=user, question_id=question, status=status)
                .on_conflict_do_update(
                    index_elements=["user_id", "question_id"],
                    set_={"status": status},
                )
            )
            await self.session.execute(stmt)

    @repository_handler
    async def delete(self, question: BaseIdType) -> Question:
        """Delete question by id and return deleted entity."""
        async with transaction_manager(self.session):
            stmt = delete(Question).where(Question.id == question).returning(Question)
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Question, question)
            return row

    @repository_handler
    async def create_multiple(self, questions_by_module: dict[BaseIdType, list[dict]]) -> list[Question]:
        """Create multiple questions across modules."""
        async with transaction_manager(self.session):
            module_ids = list(questions_by_module.keys())
            max_stmt = (
                select(Question.module_id, func.max(Question.order_index))
                .where(Question.module_id.in_(module_ids))
                .group_by(Question.module_id)
            )
            max_result = await self.session.execute(max_stmt)
            max_by_module: dict[BaseIdType, int] = {row[0]: row[1] for row in max_result.fetchall()}
            all_questions: list[dict] = []
            for module_id, questions in questions_by_module.items():
                start_index = max_by_module.get(module_id, -1) + 1
                for i, q in enumerate(questions):
                    q["order_index"] = start_index + i
                    all_questions.append(q)
            insert_stmt = insert(Question).values(all_questions).returning(Question)
            result = await self.session.execute(insert_stmt)
            return list(result.scalars().all())

    @repository_handler
    async def link_concept(self, question: BaseIdType, concept: BaseIdType) -> None:
        """Link concept to question."""
        async with transaction_manager(self.session):
            stmt = insert(QuestionConcept).values(
                question_id=question,
                concept_id=concept,
            )
            await self.session.execute(stmt)

    @repository_handler
    async def unlink_concept(self, question: BaseIdType, concept: BaseIdType) -> None:
        """Unlink concept from question."""
        async with transaction_manager(self.session):
            stmt = delete(QuestionConcept).where(
                QuestionConcept.question_id == question,
                QuestionConcept.concept_id == concept,
            )
            await self.session.execute(stmt)
