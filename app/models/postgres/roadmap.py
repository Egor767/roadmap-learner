import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.postgres.base import Base


class RoadMap(Base):
    __tablename__ = "roadmaps"

    road_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        SQLEnum("draft", "active", "archived", name="roadmap_status"), default="draft"
    )
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), default=func.now()
    )

    def __repr__(self):
        return (
            f"<RoadMap(id={self.road_id}, user_id={self.user_id}, title={self.title})>"
        )
