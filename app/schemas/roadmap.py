from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from core.types import BaseIdType


class BaseRoadmap(BaseModel):
    title: str
    description: str | None = None


class RoadmapCreate(BaseRoadmap):
    pass


class RoadmapUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


class RoadmapRead(BaseRoadmap):
    id: BaseIdType
    user_id: BaseIdType
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoadmapStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class RoadmapFilters(BaseModel):
    title: str | None = None
    description: str | None = None
    status: RoadmapStatus | None = None
