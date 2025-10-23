from enum import Enum

from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional


class CardCreate(BaseModel):
    term: str
    definition: Optional[str] = None
    example: Optional[str]
    comment: Optional[str] = None


class CardUpdate(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str]
    comment: Optional[str]
    status: Optional[str]


class CardInDB(BaseModel):
    card_id: uuid.UUID
    block_id: uuid.UUID
    term: str
    definition: str = None
    example: Optional[str]
    comment: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CardResponse(CardInDB):
    ...


class CardStatus(str, Enum):
    NOT_LEARNED = "not learned"
    LEARNING = "learning"
    KNOWN = "known"
    REVIEW = "review"


class CardFilters(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str] = None
    comment: Optional[str] = None
    status: Optional[CardStatus] = None

