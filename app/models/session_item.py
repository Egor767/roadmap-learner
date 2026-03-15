from sqlalchemy import UUID, Boolean, ForeignKey, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.custom_types import BaseIdType

from .base import Base
from .mixins import IdMixin, TimestampMixin
from .question_progress import QuestionStatus


class SessionItem(IdMixin, TimestampMixin, Base):
    session_id: Mapped[BaseIdType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    question_id: Mapped[BaseIdType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    hint: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
    )

    result: Mapped[QuestionStatus | None] = mapped_column(
        SQLEnum(QuestionStatus, name="question_status", create_type=False),
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, session_id={self.session_id!r}, "
            f"question_id={self.question_id!r}, result={self.result})"
        )

    def __repr__(self):
        return str(self)
