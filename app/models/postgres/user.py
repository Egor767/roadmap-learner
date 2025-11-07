from typing import List, TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .roadmap import Roadmap


class User(TimestampMixin, Base):
    email: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(20), nullable=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(50), nullable=False)

    roadmaps: Mapped[List["Roadmap"]] = relationship(back_populates="user")
    sessuinos

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.username!r})"

    def __repr__(self):
        return str(self)
