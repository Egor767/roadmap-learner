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
    async def create(self, data: dict, user: BaseIdType) -> Question:
        async with transaction_manager(self.session):
            block = (
                select(Block.id)
                .join(Roadmap, Block.roadmap_id == Roadmap.id)
                .where(Block.id == data.get("block_id"), Roadmap.user_id == user)
            )
            result = await self.session.execute(block)
            if result.scalar_one_or_none() is None:
                raise EntityNotFoundError(Block, data.get("block_id"))

            stmt = insert(Question).values(**data).returning(Question)
            result = await self.session.execute(stmt)
            row = result.scalar_one()
            return row

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
