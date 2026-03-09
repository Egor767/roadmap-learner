from sqlalchemy import Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import (
    IdMixin,
    RoadmapRelationMixin,
    TimestampMixin,
)


class Block(IdMixin, TimestampMixin, RoadmapRelationMixin, Base):
    __table_args__ = (
        UniqueConstraint("roadmap_id", "order_index", name="uq_block_roadmap_order"),
        UniqueConstraint("roadmap_id", "title", name="uq_block_roadmap_title"),
    )

    title: Mapped[str] = mapped_column(String(75), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=True)
    order_index: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, title={self.title!r}, order_index={self.order_index})"

    def __repr__(self):
        return str(self)
