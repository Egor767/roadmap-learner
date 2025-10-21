import uuid

from sqlalchemy import Column, String, DateTime, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.postgres.base import Base


class Block(Base):
    __tablename__ = "blocks"

    block_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    road_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False)
    status = Column(SQLEnum("draft", "active", "archived", name="roadmap_status"), default="draft")
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())

    def __repr__(self):
        return f"<Block(id={self.user_id}, road_id ={self.road_id}, title={self.title}, order_index={self.order_index})>"

