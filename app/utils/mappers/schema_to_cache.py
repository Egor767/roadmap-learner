import json
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def schema_to_cache(schema: T) -> str:
    """Serialize schema to cache-compatible string"""
    result = json.dumps([schema.model_dump(mode="json")], default=str)
    return result


def schemas_to_cache(schemas: list[T]) -> str:
    """Serialize list of schemas to cache-compatible string"""
    result = json.dumps([s.model_dump(mode="json") for s in schemas], default=str)
    return result
