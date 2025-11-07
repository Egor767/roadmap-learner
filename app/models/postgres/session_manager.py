from sqlalchemy import Column, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base
from .mixins import TimestampMixin


class Session(TimestampMixin, Base):
    user_id = Column(UUID(as_uuid=True), nullable=False)
    roadmap_id = Column(UUID(as_uuid=True), nullable=False)
    block_id = Column(UUID(as_uuid=True), nullable=True)

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
