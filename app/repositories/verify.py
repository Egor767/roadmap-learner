from typing import TYPE_CHECKING

from sqlalchemy import select

from app.core.custom_exceptions import EntityNotFoundError
from app.core.custom_types import BaseIdType
from app.core.handlers import repository_handler
from app.models import Concept, Module, Question, Roadmap, Session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class VerifyRepository:
    """Ownership verification repository for hierarchical resource access control."""

    def __init__(self, session: "AsyncSession"):
        self.session = session

    @repository_handler
    async def verify_roadmap(self, roadmap: BaseIdType, user: BaseIdType) -> Roadmap:
        """Verify that roadmap belongs to user and return it."""
        stmt = select(Roadmap).where(Roadmap.id == roadmap, Roadmap.user_id == user)
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Roadmap, roadmap)
        return row

    @repository_handler
    async def verify_module(self, module: BaseIdType, user: BaseIdType) -> Module:
        """Verify that module belongs to user through roadmap and return it."""
        stmt = (
            select(Module)
            .join(Roadmap, Module.roadmap_id == Roadmap.id)
            .where(Module.id == module, Roadmap.user_id == user)
        )
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Module, module)
        return row

    @repository_handler
    async def verify_modules(self, modules: list[BaseIdType], user: BaseIdType) -> None:
        """Verify that all modules belong to user through roadmap."""
        stmt = (
            select(Module.id)
            .join(Roadmap, Module.roadmap_id == Roadmap.id)
            .where(Module.id.in_(modules), Roadmap.user_id == user)
        )
        result = await self.session.execute(stmt)
        valid = {row[0] for row in result.fetchall()}
        missing = set(modules) - valid
        if missing:
            raise EntityNotFoundError(Module, missing.pop())

    @repository_handler
    async def verify_question(self, question: BaseIdType, user: BaseIdType) -> Question:
        """Verify that question belongs to user through module and roadmap and return it."""
        stmt = (
            select(Question)
            .join(Module, Question.module_id == Module.id)
            .join(Roadmap, Module.roadmap_id == Roadmap.id)
            .where(Question.id == question, Roadmap.user_id == user)
        )
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Question, question)
        return row

    @repository_handler
    async def verify_concept(self, concept: BaseIdType, user: BaseIdType) -> Concept:
        """Verify that concept belongs to user through roadmap and return it."""
        stmt = (
            select(Concept)
            .join(Roadmap, Concept.roadmap_id == Roadmap.id)
            .where(Concept.id == concept, Roadmap.user_id == user)
        )
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Concept, concept)
        return row

    @repository_handler
    async def verify_session(self, session: BaseIdType, user: BaseIdType) -> Session:
        """Verify that session belongs to user and return it."""
        stmt = select(Session).where(Session.id == session, Session.user_id == user)
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            raise EntityNotFoundError(Session, session)
        return row
