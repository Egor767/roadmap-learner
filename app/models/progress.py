import enum

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.custom_types import BaseIdType

from .base import Base
from .mixins import TimestampMixin


class QuestionStatus(str, enum.Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    REVIEW = "review"


class UserQuestionProgress(Base, TimestampMixin):
    __tablename__ = "user_question_progress"

    user_id: Mapped[BaseIdType] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    question_id: Mapped[BaseIdType] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    status: Mapped[QuestionStatus] = mapped_column(
        Enum(QuestionStatus, name="question_status"),
        nullable=False,
    )

    def __str__(self):
        return f"{self.__class__.__name__}(user={self.user_id}, question={self.question_id}), status={self.status}"

    def __repr__(self):
        return str(self)
