import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.postgres.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password = Column(
        String(255),
        nullable=False
    )
    username = Column(
        String(100),
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        default=func.now()
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

