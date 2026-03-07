from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.custom_types import BaseIdType

from .base import Base


class QuestionCard(Base):
    question_id: Mapped[BaseIdType] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    card_id: Mapped[BaseIdType] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE"),
        primary_key=True,
    )

    def __str__(self):
        return f"{self.__class__.__name__}(question={self.question_id}, card={self.card_id})"

    def __repr__(self):
        return str(self)
