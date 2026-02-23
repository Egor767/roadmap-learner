from typing import TypeVar

from pydantic import BaseModel

from app.models import (
    Block,
    Card,
    Roadmap,
    User,
)
from app.models.session import Session
from app.schemas.block import BlockRead
from app.schemas.card import CardRead
from app.schemas.roadmap import RoadmapRead
from app.schemas.session import SessionRead
from app.schemas.user import UserRead

T = TypeVar("T", bound=BaseModel)


def orm_to_schema(schema_cls: type[T], orm_obj) -> T:
    return schema_cls.model_validate(orm_obj)


def orm_list_to_schemas(schema_cls: type[T], orm_list: list) -> list[T]:
    return [schema_cls.model_validate(obj) for obj in orm_list]


def user_orm_to_model(db_user: User | None) -> UserRead | None:
    if db_user:
        return UserRead.model_validate(db_user)
    return


def roadmap_orm_to_model(db_roadmap: Roadmap | None) -> RoadmapRead | None:
    if db_roadmap:
        return RoadmapRead.model_validate(db_roadmap)
    return None


def block_orm_to_model(db_block: Block | None) -> BlockRead | None:
    if db_block:
        return BlockRead.model_validate(db_block)
    return


def card_orm_to_model(db_card: Card | None) -> CardRead | None:
    if db_card:
        return CardRead.model_validate(db_card)
    return


def session_orm_to_model(db_session: Session | None) -> SessionRead | None:
    if db_session:
        return SessionRead.model_validate(db_session)
    return
