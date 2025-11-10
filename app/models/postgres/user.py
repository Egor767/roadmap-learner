from typing import List, TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, IdMixin
from app.core.types import BaseIdType

if TYPE_CHECKING:
    from .roadmap import Roadmap
    from .session_manager import Session
    from .access_token import AccessToken


class User(IdMixin, TimestampMixin, Base, SQLAlchemyBaseUserTable[BaseIdType]):
    username: Mapped[str] = mapped_column(String(20), nullable=True, unique=True)

    roadmaps: Mapped[List["Roadmap"]] = relationship(back_populates="user")
    sessions: Mapped[List["Session"]] = relationship(back_populates="user")
    tokens: Mapped[List["AccessToken"]] = relationship(back_populates="user")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.username!r})"

    def __repr__(self):
        return str(self)
