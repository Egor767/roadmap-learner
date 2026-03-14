from datetime import datetime

from sqlalchemy import ARRAY, UUID, Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.custom_types import BaseIdType

from .base import Base
from .mixins import (
    IdMixin,
    RoadmapRelationMixin,
    TimestampMixin,
    UserRelationMixin,
)


class Session(
    IdMixin,
    TimestampMixin,
    UserRelationMixin,
    RoadmapRelationMixin,
    Base,
):
    mode: Mapped[str] = mapped_column(
        SQLEnum(
            "exam",
            "repeat",
            name="session_mode",
        ),
        nullable=False,
    )

    auto_check: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
    )

    block_id: Mapped[BaseIdType] = mapped_column(
        UUID,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        SQLEnum(
            "active",
            "completed",
            "abandoned",
            name="session_status",
        ),
        default="active",
    )

    questions: Mapped[list[BaseIdType] | None] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=True,
        default=list,
    )

    index: Mapped[int] = mapped_column(
        default=0,
    )

    correct_answers: Mapped[int] = mapped_column(
        default=0,
    )

    incorrect_answers: Mapped[int] = mapped_column(
        default=0,
    )

    review_answers: Mapped[int] = mapped_column(
        default=0,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, user_id={self.user_id!r}, "
            f"mode={self.mode}, status={self.status}, auto_check={self.auto_check}"
        )

    def __repr__(self):
        return str(self)
