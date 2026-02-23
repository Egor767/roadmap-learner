import json
from typing import TypeVar, Type

from pydantic import BaseModel

from app.schemas.block import BlockRead
from app.schemas.roadmap import RoadmapRead
from app.schemas.card import CardRead


T = TypeVar("T", bound=BaseModel)


def cache_to_schema(schema_cls: Type[T], cached: str) -> T:
    data_list = json.loads(cached)
    return [schema_cls.model_validate(data) for data in data_list][0]


def cache_to_schemas(schema_cls: Type[T], cached: str) -> list[T]:
    data_list = json.loads(cached)
    return [schema_cls.model_validate(data) for data in data_list]


def roadmap_cache_to_models(
    cached: str,
) -> list[RoadmapRead]:
    data_list = json.loads(cached)
    return [RoadmapRead.model_validate(data) for data in data_list]


def block_cache_to_models(
    cached: str,
) -> list[BlockRead]:
    data_list = json.loads(cached)
    return [BlockRead.model_validate(data) for data in data_list]


def card_cache_to_models(
    cached: str,
) -> list[CardRead]:
    data_list = json.loads(cached)
    return [CardRead.model_validate(data) for data in data_list]
