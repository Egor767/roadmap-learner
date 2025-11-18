from typing import List, TYPE_CHECKING

from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base
from .mixins import UserRelationMixin, TimestampMixin, IdMixin

if TYPE_CHECKING:
    from .block import Block


class Roadmap(IdMixin, TimestampMixin, UserRelationMixin, Base):
    _user_back_populates = "roadmaps"

    title: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(
        SQLEnum(
            "draft",
            "active",
            "archived",
            name="roadmap_status",
        ),
        default="draft",
    )

    blocks: Mapped[List["Block"]] = relationship(back_populates="roadmap")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, title={self.title!r}), status={self.status}"

    def __repr__(self):
        return str(self)
