import enum

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import CardRelationMixin, TimestampMixin, UserRelationMixin


class CardStatus(str, enum.Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    REPEAT = "repeat"


class UserCardProgress(Base, TimestampMixin, UserRelationMixin, CardRelationMixin):
    __tablename__ = "user_card_progress"

    _user_id_primary_key = True
    _card_id_primary_key = True

    status: Mapped[CardStatus] = mapped_column(
        Enum(CardStatus, name="card_status"),
        nullable=False,
    )

    def __str__(self):
        return f"{self.__class__.__name__}(user={self.user_id}, card={self.card_id}, status={self.status})"

    def __repr__(self):
        return str(self)
