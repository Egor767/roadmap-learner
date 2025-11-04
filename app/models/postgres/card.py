import uuid

from sqlalchemy import Column, String, DateTime, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.postgres.base import Base


class Card(Base):
    __tablename__ = "cards"

    card_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    block_id = Column(UUID(as_uuid=True), nullable=False)
    term = Column(String(255), nullable=False)
    definition = Column(Text, nullable=False)
    example = Column(Text)
    comment = Column(Text)
    status = Column(
        SQLEnum("unknown", "known", "review", name="card_status"), default="unknown"
    )
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), default=func.now()
    )

    def __repr__(self):
        return (
            f"<Card(id={self.card_id}, "
            f"block_id ={self.block_id}, "
            f"term={self.term}, "
            f"status={self.status})>"
        )
