from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.custom_types import BaseIdType


class BaseBlock(BaseModel):
    title: str = Field(..., max_length=75)
    description: str | None = Field(default=None, max_length=300)

    model_config = ConfigDict(from_attributes=True)


class BlockCreate(BaseBlock):
    roadmap_id: BaseIdType
    position: Literal["start", "end"] | None = None
    previous: BaseIdType | None = None

    @model_validator(mode="after")
    def validate_position(self):
        if self.position is not None and self.previous is not None:
            raise ValueError("Нельзя одновременно указывать position и previous")

        if self.position is None and self.previous is None:
            self.position = "end"

        return self


class BlockUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=75)
    description: str | None = Field(default=None, max_length=300)
    order_index: float | None = None
    roadmap_id: BaseIdType | None = None


class BlockMove(BaseModel):
    roadmap_id: BaseIdType
    previous: BaseIdType | None = None


class BlockRead(BaseBlock):
    id: BaseIdType
    roadmap_id: BaseIdType
    order_index: float
    created_at: datetime
    updated_at: datetime


class BlockFilters(BaseModel):
    roadmap_id: BaseIdType | None = None
    title: str | None = None
    description: str | None = None
    order_index: float | None = None
