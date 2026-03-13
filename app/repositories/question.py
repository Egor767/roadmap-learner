from typing import Literal

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
from app.models import Block, Question, Roadmap
from app.repositories import BaseRepository


class QuestionRepository(BaseRepository):
    @repository_handler
    async def get_all(self) -> list[Question]:
        stmt = select(Question)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def get_by_id(self, question: BaseIdType, user: BaseIdType) -> Question:
        stmt = (
            select(Question)
            .join(Block, Question.block_id == Block.id)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Question.id == question, Roadmap.user_id == user)
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Question, question)
        return row

    @repository_handler
    async def get_by_filters(self, filters: dict, user: BaseIdType) -> list[Question]:
        stmt = (
            select(Question)
            .join(Block, Question.block_id == Block.id)
            .join(Roadmap, Block.roadmap_id == Roadmap.id)
            .where(Roadmap.user_id == user)
        )
        if filters.get("roadmap_id", None) is not None:
            stmt = stmt.where(Block.roadmap_id == filters.pop("roadmap_id"))

        for field_name, value in filters.items():
            column = getattr(Question, field_name)
            if isinstance(value, list):
                stmt = stmt.where(column.in_(value))
            else:
                stmt = stmt.where(column == value)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())
        return rows

    @repository_handler
    async def create(
        self,
        block_id: BaseIdType,
        data: dict,
        user: BaseIdType,
        position: Literal["start", "end"] = "end",
        previous: BaseIdType | None = None,
    ) -> Question:
        async with transaction_manager(self.session):
            block_check = (
                select(Block.id)
                .join(Roadmap, Block.roadmap_id == Roadmap.id)
                .where(Block.id == block_id, Roadmap.user_id == user)
            )
            if (await self.session.execute(block_check)).scalar_one_or_none() is None:
                raise EntityNotFoundError(Block, block_id)

            if previous is not None:
                prev_stmt = select(Question.order_index).where(
                    Question.id == previous,
                    Question.block_id == block_id,
                )
                prev_index = (await self.session.execute(prev_stmt)).scalar_one_or_none()
                if prev_index is None:
                    raise EntityNotFoundError(Question, previous)

                await self.session.execute(
                    update(Question)
                    .where(Question.block_id == block_id, Question.order_index > prev_index)
                    .values(order_index=Question.order_index + 1)
                )
                data["order_index"] = prev_index + 1

            elif position == "start":
                await self.session.execute(
                    update(Question).where(Question.block_id == block_id).values(order_index=Question.order_index + 1)
                )
                data["order_index"] = 0

            else:
                max_stmt = select(func.max(Question.order_index)).where(Question.block_id == block_id)
                max_index = (await self.session.execute(max_stmt)).scalar()
                data["order_index"] = (max_index + 1) if max_index is not None else 0

            stmt = insert(Question).values(**data).returning(Question)
            return (await self.session.execute(stmt)).scalar_one()

    @repository_handler
    async def move(
        self,
        block_id: BaseIdType,
        question_id: BaseIdType,
        previous: BaseIdType | None,
        user: BaseIdType,
    ) -> Question:
        async with transaction_manager(self.session):
            stmt = select(Question).where(
                Question.id == question_id,
                Question.block_id == block_id,
                Question.block_id.in_(
                    select(Block.id)
                    .join(Roadmap, Block.roadmap_id == Roadmap.id)
                    .where(Block.id == block_id, Roadmap.user_id == user)
                ),
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
                    Question.block_id == block_id,
                )
                after_index = (await self.session.execute(prev_stmt)).scalar_one_or_none()
                if after_index is None:
                    raise EntityNotFoundError(Question, previous)

                if after_index < old_index:
                    new_index = after_index + 1
                else:
                    new_index = after_index

            if new_index == old_index:
                return row

            if new_index < old_index:
                await self.session.execute(
                    update(Question)
                    .where(
                        Question.block_id == block_id,
                        Question.order_index >= new_index,
                        Question.order_index < old_index,
                        Question.id != question_id,
                    )
                    .values(order_index=Question.order_index + 1)
                )
            else:
                await self.session.execute(
                    update(Question)
                    .where(
                        Question.block_id == block_id,
                        Question.order_index > old_index,
                        Question.order_index <= new_index,
                        Question.id != question_id,
                    )
                    .values(order_index=Question.order_index - 1)
                )

            result = await self.session.execute(
                update(Question).where(Question.id == question_id).values(order_index=new_index).returning(Question)
            )
            return result.scalar_one()

    @repository_handler
    async def update(self, question: BaseIdType, data: dict, user: BaseIdType) -> Question:
        async with transaction_manager(self.session):
            blocks = select(Block.id).join(Roadmap).where(Roadmap.user_id == user)
            stmt = (
                update(Question)
                .where(Question.id == question, Question.block_id.in_(blocks))
                .values(**data)
                .returning(Question)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Question, question)
            return row

    @repository_handler
    async def delete(self, card: BaseIdType, user: BaseIdType) -> Question:
        async with transaction_manager(self.session):
            stmt = (
                delete(Question)
                .where(
                    Question.id == card,
                    Question.block_id.in_(select(Block.id).join(Roadmap).where(Roadmap.user_id == user)),
                )
                .returning(Question)
            )
            result = await self.session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                raise EntityNotFoundError(Question, card)
            return row

    @repository_handler
    async def create_multiple(
        self,
        questions_by_block: dict[BaseIdType, list[dict]],
        user: BaseIdType,
    ) -> list[Question]:
        async with transaction_manager(self.session):
            block_ids = list(questions_by_block.keys())

            block_check = (
                select(Block.id)
                .join(Roadmap, Block.roadmap_id == Roadmap.id)
                .where(Block.id.in_(block_ids), Roadmap.user_id == user)
            )
            result = await self.session.execute(block_check)
            valid_ids = {row[0] for row in result.fetchall()}

            missing = set(block_ids) - valid_ids
            if missing:
                raise EntityNotFoundError(Block, missing.pop())

            max_stmt = (
                select(Question.block_id, func.max(Question.order_index))
                .where(Question.block_id.in_(block_ids))
                .group_by(Question.block_id)
            )
            max_result = await self.session.execute(max_stmt)
            max_by_block: dict[BaseIdType, int] = {row[0]: row[1] for row in max_result.fetchall()}

            all_questions: list[dict] = []
            for block_id, questions in questions_by_block.items():
                start_index = max_by_block.get(block_id, -1) + 1
                for i, q in enumerate(questions):
                    q["order_index"] = start_index + i
                    all_questions.append(q)

            insert_stmt = insert(Question).values(all_questions).returning(Question)
            result = await self.session.execute(insert_stmt)
            return list(result.scalars().all())
