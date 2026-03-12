from sqlalchemy import Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import (
    BlockRelationMixin,
    IdMixin,
    TimestampMixin,
)


class Question(IdMixin, TimestampMixin, BlockRelationMixin, Base):
    __table_args__ = (
        UniqueConstraint(
            "block_id",
            "order_index",
            name="uq_question_block_order",
            deferrable=True,
            initially="DEFERRED",
        ),
        UniqueConstraint("block_id", "question", name="uq_question_block_question"),
        Index("ix_question_block_order", "block_id", "order_index"),
    )

    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, question={self.question}, order_index={self.order_index})"

    def __repr__(self):
        return str(self)
