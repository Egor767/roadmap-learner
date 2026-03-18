from datetime import datetime
from typing import TYPE_CHECKING, Any

from fastapi_users import exceptions
from sqlalchemy import DateTime, ForeignKey, func, text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.core.custom_types import BaseIdType
from app.utils.generators import id_generator, server_id_generator

if TYPE_CHECKING:
    from .module import Module
    from .roadmap import Roadmap
    from .user import User


class IdMixin:
    id: Mapped[BaseIdType] = mapped_column(
        primary_key=True,
        default=id_generator,
        server_default=text(server_id_generator()),
    )

    def parse_id(self, value: Any) -> BaseIdType:
        if isinstance(value, BaseIdType):
            return value
        try:
            return BaseIdType(value)
        except ValueError as e:
            raise exceptions.InvalidID() from e


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        default=func.now(),
        server_default=func.now(),
    )


class UserRelationMixin:
    _user_id_nullable: bool = False
    _user_id_unique: bool = False
    _user_id_primary_key: bool = False
    _user_back_populates: str | None = None

    @declared_attr
    def user_id(cls) -> Mapped[BaseIdType]:
        return mapped_column(
            ForeignKey("users.id", ondelete="CASCADE"),
            unique=cls._user_id_unique,
            nullable=cls._user_id_nullable,
            primary_key=cls._user_id_primary_key,
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship(
            "User",
            back_populates=cls._user_back_populates,
        )


class RoadmapRelationMixin:
    _roadmap_id_nullable: bool = False
    _roadmap_id_unique: bool = False
    _roadmap_id_primary_key: bool = False
    _roadmap_back_populates: str | None = None

    @declared_attr
    def roadmap_id(cls) -> Mapped[BaseIdType]:
        return mapped_column(
            ForeignKey("roadmaps.id", ondelete="CASCADE"),
            unique=cls._roadmap_id_unique,
            nullable=cls._roadmap_id_nullable,
            primary_key=cls._roadmap_id_primary_key,
        )

    @declared_attr
    def roadmap(cls) -> Mapped["Roadmap"]:
        return relationship(
            "Roadmap",
            back_populates=cls._roadmap_back_populates,
        )


class ModuleRelationMixin:
    _module_id_nullable: bool = False
    _module_id_unique: bool = False
    _module_back_populates: str | None = None

    @declared_attr
    def module_id(cls) -> Mapped[BaseIdType]:
        return mapped_column(
            ForeignKey("modules.id", ondelete="CASCADE"),
            unique=cls._module_id_unique,
            nullable=cls._module_id_nullable,
        )

    @declared_attr
    def module(cls) -> Mapped["Module"]:
        return relationship(
            "Module",
            back_populates=cls._module_back_populates,
        )


class ConceptRelationMixin:
    _concept_id_nullable: bool = False
    _concept_id_unique: bool = False
    _concept_id_primary_key: bool = False
    _concept_back_populates: str | None = None

    @declared_attr
    def concept_id(cls) -> Mapped[BaseIdType]:
        return mapped_column(
            ForeignKey("concepts.id", ondelete="CASCADE"),
            unique=cls._concept_id_unique,
            nullable=cls._concept_id_nullable,
            primary_key=cls._concept_id_primary_key,
        )

    @declared_attr
    def concept(cls) -> Mapped["Module"]:
        return relationship(
            "Concept",
            back_populates=cls._concept_back_populates,
        )


class QuestionRelationMixin:
    _question_id_nullable: bool = False
    _question_id_unique: bool = False
    _question_id_primary_key: bool = False
    _question_back_populates: str | None = None

    @declared_attr
    def question_id(cls) -> Mapped[BaseIdType]:
        return mapped_column(
            ForeignKey("questions.id", ondelete="CASCADE"),
            unique=cls._question_id_unique,
            nullable=cls._question_id_nullable,
            primary_key=cls._question_id_primary_key,
        )

    @declared_attr
    def question(cls) -> Mapped["Block"]:
        return relationship(
            "Question",
            back_populates=cls._question_back_populates,
        )
