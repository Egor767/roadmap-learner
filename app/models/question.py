from sqlalchemy import Float, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import (
    BlockRelationMixin,
    IdMixin,
    TimestampMixin,
)


class Question(IdMixin, TimestampMixin, BlockRelationMixin, Base):
    __table_args__ = (UniqueConstraint("block_id", "order_index", name="uq_question_block_order"),)

    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, question={self.question}, order_index={self.order_index})"

    def __repr__(self):
        return str(self)
