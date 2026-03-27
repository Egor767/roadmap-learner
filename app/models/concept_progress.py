from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import ConceptStatus

from .base import Base
from .mixins import ConceptRelationMixin, TimestampMixin, UserRelationMixin


class ConceptProgress(Base, TimestampMixin, UserRelationMixin, ConceptRelationMixin):
    __tablename__ = "concept_progress"

    _user_id_primary_key = True
    _concept_id_primary_key = True

    status: Mapped[ConceptStatus] = mapped_column(
        Enum(ConceptStatus, name="card_status"),
        nullable=False,
    )

    def __str__(self):
        return f"{self.__class__.__name__}(user={self.user_id}, concept={self.concept_id}, status={self.status})"

    def __repr__(self):
        return str(self)
