from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import BaseIdType


class BaseBlock(BaseModel):
    title: str = Field(..., max_length=75)
    description: str | None = Field(default=None, max_length=300)

    model_config = ConfigDict(from_attributes=True)


class BlockCreate(BaseBlock):
    order_index: float
    roadmap_id: BaseIdType


class BlockUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=75)
    description: str | None = Field(default=None, max_length=300)
    order_index: float | None = None
    roadmap_id: BaseIdType | None = None


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
