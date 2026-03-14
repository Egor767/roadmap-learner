import enum

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import QuestionRelationMixin, TimestampMixin, UserRelationMixin


class QuestionStatus(str, enum.Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    REPEAT = "repeat"


class UserQuestionProgress(Base, TimestampMixin, UserRelationMixin, QuestionRelationMixin):
    __tablename__ = "user_question_progress"

    _user_id_primary_key = True
    _question_id_primary_key = True

    status: Mapped[QuestionStatus] = mapped_column(
        Enum(QuestionStatus, name="question_status", create_type=False),
        nullable=False,
    )

    def __str__(self):
        return f"{self.__class__.__name__}(user={self.user_id}, question={self.question_id}, status={self.status})"

    def __repr__(self):
        return str(self)
