from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import (
    IdMixin,
    ModuleRelationMixin,
    TimestampMixin,
)


class Question(IdMixin, TimestampMixin, ModuleRelationMixin, Base):
    __table_args__ = (
        UniqueConstraint("module_id", "question", name="uq_question_module_question"),
    )

    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=True)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, question={self.question})"

    def __repr__(self):
        return str(self)
