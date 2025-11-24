import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

from app.core.types import BaseIdType
from app.schemas.card import CardStatus


class SessionSettings(BaseModel): ...


class SessionMode(str, Enum):
    REVIEW = "review"
    EXAM = "exam"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionCreate(BaseModel):
    roadmap_id: BaseIdType
    block_id: Optional[BaseIdType] = None
    mode: SessionMode
    settings: SessionSettings = SessionSettings()


class SessionInDB(BaseModel):
    id: BaseIdType
    user_id: BaseIdType
    roadmap_id: BaseIdType
    block_id: Optional[BaseIdType] = None

    mode: SessionMode

    status: SessionStatus
    card_queue: List[BaseIdType] = []
    current_card_index: int

    correct_answers: int
    incorrect_answers: int
    review_answers: int

    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionResponse(SessionInDB): ...


class SessionUpdate(BaseModel):
    status: Optional[SessionStatus] = None
    current_card_index: Optional[int] = None
    correct_answers: Optional[int] = None
    incorrect_answers: Optional[int] = None
    review_answers: Optional[int] = None


class SessionFilters(BaseModel):
    roadmap_id: Optional[BaseIdType] = None
    block_id: Optional[uuid.UUID] = None
    mode: Optional[SessionMode] = None
    status: Optional[SessionStatus] = None


class SessionResult(BaseModel):
    id: BaseIdType
    user_id: BaseIdType
    roadmap_id: BaseIdType
    mode: SessionMode
    total_cards: int
    correct_answers: int
    incorrect_answers: int
    review_answers: int
    accuracy_percentage: float
    completed_at: datetime


class SubmitAnswerRequest(BaseModel):
    card_id: BaseIdType
    answer: CardStatus
