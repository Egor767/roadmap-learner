from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Ensure title is not explicitly set to null"""
        if v is None:
            raise ValueError("Field 'title' cannot be null")
        return v

    @model_validator(mode="after")
    def validate(self) -> "RoadmapUpdate":
        """Ensure at least one field is provided for update"""
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update")
        return self


class RoadmapRead(BaseRoadmap):
    id: BaseIdType
    created_at: datetime
    updated_at: datetime


class RoadmapFilters(BaseModel):
    title: str | None = None
    description: str | None = None
