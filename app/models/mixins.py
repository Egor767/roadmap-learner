from datetime import datetime
from typing import TYPE_CHECKING, Any

from fastapi_users import exceptions
from sqlalchemy import ForeignKey, DateTime, func, text
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship

from app.core.types import BaseIdType
from app.utils.generators import server_id_generator, id_generator

if TYPE_CHECKING:
    from .user import User
    from .roadmap import Roadmap
    from .block import Block


class IdMixin:
    id: Mapped[BaseIdType] = mapped_column(
        primary_key=True,
        default=id_generator(),
        server_default=text(server_id_generator()),
    )

    def parse_id(self, value: Any) -> BaseIdType:
        if isinstance(value, BaseIdType):
            return value
        try:
            return BaseIdType(value)
        except ValueError as e:
            raise exceptions.InvalidID() from e


class UserRelationMixin:
    _user_id_nullable: bool = False
    _user_id_unique: bool = False
    _user_back_populates: str | None = None

    @declared_attr
    def user_id(cls) -> Mapped[BaseIdType]:
        return mapped_column(
            ForeignKey("users.id"),
            unique=cls._user_id_unique,
            nullable=cls._user_id_nullable,
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship(
            "User",
            back_populates=cls._user_back_populates,
        )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        default=func.now(),
        server_default=func.now(),
    )


class RoadmapRelationMixin:
    _roadmap_id_nullable: bool = False
    _roadmap_id_unique: bool = False
    _roadmap_back_populates: str | None = None

    @declared_attr
    def roadmap_id(cls) -> Mapped[BaseIdType]:
        return mapped_column(
            ForeignKey("roadmaps.id"),
            unique=cls._roadmap_id_unique,
            nullable=cls._roadmap_id_nullable,
        )

    @declared_attr
    def roadmap(cls) -> Mapped["Roadmap"]:
        return relationship(
            "Roadmap",
            back_populates=cls._roadmap_back_populates,
        )


class BlockRelationMixin:
    _block_id_nullable: bool = False
    _block_id_unique: bool = False
    _block_back_populates: str | None = None

    @declared_attr
    def block_id(cls) -> Mapped[BaseIdType]:
        return mapped_column(
            ForeignKey("blocks.id"),
            unique=cls._block_id_unique,
            nullable=cls._block_id_nullable,
        )

    @declared_attr
    def block(cls) -> Mapped["Block"]:
        return relationship(
            "Block",
            back_populates=cls._block_back_populates,
        )
