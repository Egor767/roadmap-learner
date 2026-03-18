from sqlalchemy import Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import (
    IdMixin,
    RoadmapRelationMixin,
    TimestampMixin,
)


class Module(IdMixin, TimestampMixin, RoadmapRelationMixin, Base):
    __table_args__ = (
        UniqueConstraint(
            "roadmap_id",
            "order_index",
            name="uq_module_roadmap_order",
            deferrable=True,
            initially="DEFERRED",
        ),
        UniqueConstraint("roadmap_id", "title", name="uq_module_roadmap_title"),
        Index("ix_module_roadmap_order", "roadmap_id", "order_index"),
    )

    title: Mapped[str] = mapped_column(String(75), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, title={self.title!r}, order_index={self.order_index})"

    def __repr__(self):
        return str(self)
