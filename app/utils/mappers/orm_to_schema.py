from typing import TypeVar

from pydantic import BaseModel

from app.models import (
    User,
)
from app.schemas.user import UserRead

T = TypeVar("T", bound=BaseModel)


def orm_to_schema(schema_cls: type[T], orm_obj) -> T:
    return schema_cls.model_validate(orm_obj)


def orm_list_to_schemas(schema_cls: type[T], orm_list: list) -> list[T]:
    return [schema_cls.model_validate(obj) for obj in orm_list]


def user_orm_to_model(db_user: User) -> UserRead:
    return UserRead.model_validate(db_user)


def orm_to_schema_status(schema_cls: type[T], orm, status) -> T:
    return orm_to_schema(schema_cls, orm).model_copy(update={"status": status})


def orm_list_to_schemas_statuses(schema_cls: type[T], orm_list, statuses) -> list[T]:
    return [orm_to_schema(schema_cls, item).model_copy(update={"status": statuses[item.id]}) for item in orm_list]
