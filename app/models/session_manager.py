from sqlalchemy import Column, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base
from .mixins import (
    TimestampMixin,
    UserRelationMixin,
    RoadmapRelationMixin,
    BlockRelationMixin,
    IdMixin,
)


class Session(
    IdMixin,
    TimestampMixin,
    UserRelationMixin,
    RoadmapRelationMixin,
    BlockRelationMixin,
    Base,
):
    _user_back_populates = "sessions"
    _roadmap_back_populates = None
    _block_back_populates = None
    _block_id_nullable = True

    mode = Column(SQLEnum("review", "exam", name="session_mode"), nullable=False)

    status = Column(
        SQLEnum("active", "completed", "abandoned", name="session_status"),
        default="active",
    )
    card_queue = Column(JSONB, nullable=True, default=list)
    current_card_index = Column(Integer, default=0)

    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    review_answers = Column(Integer, default=0)

    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"user_id={self.user_id!r}), "
            f"mode={self.mode}, "
            f"status={self.status}"
        )

    def __repr__(self):
        return str(self)
