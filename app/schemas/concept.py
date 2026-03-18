from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType


class ConceptStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    REPEAT = "repeat"


class BaseConcept(BaseModel):
    term: str = Field(..., max_length=100)
    definition: str = Field(..., max_length=1000)

    model_config = ConfigDict(from_attributes=True)


class ConceptCreate(BaseConcept):
    example: str | None = Field(default=None, max_length=1000)
    comment: str | None = Field(default=None, max_length=500)
    roadmap_id: BaseIdType


class ConceptUpdate(BaseModel):
    term: str | None = Field(default=None, max_length=100)
    definition: str | None = Field(default=None, max_length=1000)
    example: str | None = Field(default=None, max_length=1000)
    comment: str | None = Field(default=None, max_length=500)


class ConceptRead(BaseConcept):
    id: BaseIdType
    roadmap_id: BaseIdType
    example: str | None = None
    comment: str | None = None
    created_at: datetime
    updated_at: datetime


class ConceptFilters(BaseModel):
    roadmap_id: BaseIdType | None = None
    term: str | None = None
    definition: str | None = None
    example: str | None = None
    comment: str | None = None
