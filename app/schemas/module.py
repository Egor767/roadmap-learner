from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.custom_types import BaseIdType


class BaseModule(BaseModel):
    title: str = Field(..., max_length=75)
    description: str | None = Field(default=None, max_length=300)

    model_config = ConfigDict(from_attributes=True)


class ModuleCreate(BaseModule):
    roadmap_id: BaseIdType
    position: Literal["start", "end"] | None = None
    previous: BaseIdType | None = None

    @model_validator(mode="after")
    def validate_position(self):
        if self.position is not None and self.previous is not None:
            raise ValueError("Cannot set both fields at the same time: position and previous")

        if self.position is None and self.previous is None:
            self.position = "end"

        return self


class ModuleUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=75)
    description: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def validate(self) -> "ModuleUpdate":
        """Ensure at least one field is provided for update"""
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update")
        return self

    def dump(self) -> dict:
        """Return update data excluding unset and non-nullable null fields"""
        data = self.model_dump(exclude_unset=True)
        nullable = {"description"}
        result = {k: v for k, v in data.items() if v is not None or k in nullable}
        return result


class ModuleMove(BaseModel):
    previous: BaseIdType | None = None


class ModuleRead(BaseModule):
    id: BaseIdType
    roadmap_id: BaseIdType
    order_index: int
    created_at: datetime
    updated_at: datetime


class ModuleFilters(BaseModel):
    roadmap_id: BaseIdType | None = None
    title: str | None = None
    description: str | None = None
    order_index: int | None = None


class ModuleConfirmRequest(BaseModel):
    roadmap_id: BaseIdType
    modules: list[BaseModule] = Field(..., min_length=1, max_length=20)
