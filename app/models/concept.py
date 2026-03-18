from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import (
    IdMixin,
    RoadmapRelationMixin,
    TimestampMixin,
)


class Concept(IdMixin, TimestampMixin, RoadmapRelationMixin, Base):
    __table_args__ = (UniqueConstraint("roadmap_id", "term", name="uq_concept_roadmap_term"),)

    term: Mapped[str] = mapped_column(String(100), nullable=False)
    definition: Mapped[str] = mapped_column(String(1000), nullable=False)
    example: Mapped[str] = mapped_column(String(1000), nullable=True)
    comment: Mapped[str] = mapped_column(String(500), nullable=True)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, term={self.term!r})"

    def __repr__(self):
        return str(self)
