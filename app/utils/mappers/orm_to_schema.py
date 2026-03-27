from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def orm_to_schema(schema_cls: type[T], orm_obj) -> T:
    return schema_cls.model_validate(orm_obj)


def orms_to_schemas(schema_cls: type[T], orm_list: list) -> list[T]:
    return [schema_cls.model_validate(obj) for obj in orm_list]
