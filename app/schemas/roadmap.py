from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType


class RoadmapStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class BaseRoadmap(BaseModel):
    title: str = Field(..., max_length=100)
    description: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class RoadmapCreate(BaseRoadmap):
    pass


class RoadmapUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    status: RoadmapStatus | None = None


class RoadmapRead(BaseRoadmap):
    id: BaseIdType
    user_id: BaseIdType
    status: RoadmapStatus
    created_at: datetime
    updated_at: datetime


class RoadmapFilters(BaseModel):
    title: str | None = None
    description: str | None = None
    status: RoadmapStatus | None = None
