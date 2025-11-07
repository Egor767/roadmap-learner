from typing import List, TYPE_CHECKING

from sqlalchemy import String, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base
from .mixins import RoadmapRelationMixin, TimestampMixin

if TYPE_CHECKING:
    from .card import Card


class Block(TimestampMixin, RoadmapRelationMixin, Base):
    _roadmap_back_populates = "blocks"

    title: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(30))
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum("draft", "active", "archived", name="block_status"), default="draft"
    )

    cards: Mapped[List["Card"]] = relationship(back_populates="block")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, title={self.title!r}), status={self.status}"

    def __repr__(self):
        return str(self)
