from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType


class BaseCard(BaseModel):
    term: str = Field(..., max_length=100)
    definition: str = Field(..., max_length=1000)

    model_config = ConfigDict(from_attributes=True)


class CardCreate(BaseCard):
    example: str | None = Field(default=None, max_length=1000)
    comment: str | None = Field(default=None, max_length=500)
    roadmap_id: BaseIdType


class CardUpdate(BaseModel):
    term: str | None = Field(default=None, max_length=100)
    definition: str | None = Field(default=None, max_length=1000)
    example: str | None = Field(default=None, max_length=1000)
    comment: str | None = Field(default=None, max_length=500)


class CardRead(BaseCard):
    id: BaseIdType
    roadmap_id: BaseIdType
    example: str | None = None
    comment: str | None = None
    created_at: datetime
    updated_at: datetime


class CardFilters(BaseModel):
    term: str | None = None
    definition: str | None = None
    example: str | None = None
    comment: str | None = None
