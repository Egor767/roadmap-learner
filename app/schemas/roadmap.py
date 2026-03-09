from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType


class BaseRoadmap(BaseModel):
    title: str = Field(..., max_length=100)
    description: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class RoadmapCreate(BaseRoadmap):
    pass


class RoadmapUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class RoadmapRead(BaseRoadmap):
    id: BaseIdType
    user_id: BaseIdType
    created_at: datetime
    updated_at: datetime


class RoadmapFilters(BaseModel):
    title: str | None = None
    description: str | None = None
