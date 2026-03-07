from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import IdMixin, TimestampMixin, UserRelationMixin


class Roadmap(IdMixin, TimestampMixin, UserRelationMixin, Base):
    __table_args__ = (UniqueConstraint("user_id", "title", name="uq_roadmap_user_title"),)

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, title={self.title!r}), status={self.status}"

    def __repr__(self):
        return str(self)
