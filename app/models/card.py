from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import BlockRelationMixin, TimestampMixin, IdMixin


class Card(IdMixin, TimestampMixin, BlockRelationMixin, Base):
    # _block_back_populates = "cards"

    term: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    definition: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    example: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )
    comment: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(
            "unknown",
            "known",
            "review",
            name="card_status",
        ),
        default="unknown",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, term={self.term!r}), status={self.status}"

    def __repr__(self):
        return str(self)
