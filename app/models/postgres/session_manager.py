import uuid

from sqlalchemy import Column, DateTime, Integer, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.db.postgres.base import Base


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    roadmap_id = Column(UUID(as_uuid=True), nullable=False)
    block_id = Column(UUID(as_uuid=True), nullable=True)

    mode = Column(SQLEnum("review", "exam", name="session_mode"), nullable=False)

    status = Column(SQLEnum("active", "completed", "abandoned", name="session_status"), default="active")
    card_queue = Column(JSONB, nullable=True, default=list)
    current_card_index = Column(Integer, default=0)

    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    review_answers = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return (f"<Session(id={self.session_id}, "
                f"user_id={self.user_id}, "
                f"mode={self.mode}, "
                f"status={self.status})>")

