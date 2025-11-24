from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase as SQLAlchemyUserDatabaseGeneric,
)
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import BaseIdType
from .base import Base
from .mixins import TimestampMixin, IdMixin

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyUserDatabase(SQLAlchemyUserDatabaseGeneric):
    async def get_users(self) -> list["User"]:
        statement = select(User).order_by(User.id)
        results = await self.session.scalars(statement)
        return list(results.all())


class User(IdMixin, TimestampMixin, Base, SQLAlchemyBaseUserTable[BaseIdType]):
    username: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
    )

    # roadmaps: Mapped[List["Roadmap"]] = relationship(back_populates="user")
    # sessions: Mapped[List["Session"]] = relationship(back_populates="user")
    # tokens: Mapped[List["AccessToken"]] = relationship(back_populates="user")

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, cls)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.username!r})"

    def __repr__(self):
        return str(self)
