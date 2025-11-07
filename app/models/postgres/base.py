from sqlalchemy import text
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    Mapped,
    mapped_column,
)

from app.core.types import BaseIDType


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[BaseIDType] = mapped_column(
        primary_key=True,
        default=BaseIDType,
        server_default=text("gen_random_uuid()"),
    )
