import json
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def cache_to_schema(schema_cls: type[T], cached: str) -> T:
    data_list = json.loads(cached)
    return [schema_cls.model_validate(data) for data in data_list][0]


def cache_to_schemas(schema_cls: type[T], cached: str) -> list[T]:
    data_list = json.loads(cached)
    return [schema_cls.model_validate(data) for data in data_list]
