from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.custom_types import BaseIdType
from app.core.enums import ConceptStatus


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
    status: ConceptStatus | None = None

    @model_validator(mode="after")
    def validate(self) -> "ConceptUpdate":
        """Ensure at least one field is provided for update"""
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update")
        return self


class ConceptRead(BaseConcept):
    id: BaseIdType
    roadmap_id: BaseIdType
    example: str | None = None
    comment: str | None = None
    status: ConceptStatus = ConceptStatus.UNKNOWN
    created_at: datetime
    updated_at: datetime


class ConceptFilters(BaseModel):
    roadmap_id: BaseIdType | None = None
    question_id: BaseIdType | None = None
    term: str | None = None
    definition: str | None = None
    example: str | None = None
    comment: str | None = None
    status: ConceptStatus | None = None
