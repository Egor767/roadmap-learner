from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.types import BaseIDType


class CardCreate(BaseModel):
    term: str
    definition: Optional[str] = None
    example: Optional[str]
    comment: Optional[str] = None


class CardUpdate(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str] = None
    comment: Optional[str] = None
    status: Optional[str] = None


class CardInDB(BaseModel):
    id: BaseIDType
    block_id: BaseIDType
    term: str
    definition: str = None
    example: Optional[str]
    comment: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CardResponse(CardInDB): ...


class CardStatus(str, Enum):
    UNKNOWN = "unknown"
    KNOWN = "known"
    REVIEW = "review"


class CardFilters(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str] = None
    comment: Optional[str] = None
    status: Optional[CardStatus] = None
