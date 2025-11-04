from enum import Enum
from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

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
    roadmap_id: uuid.UUID
    block_id: Optional[uuid.UUID] = None
    mode: SessionMode
    settings: SessionSettings = SessionSettings()


class SessionInDB(BaseModel):
    session_id: uuid.UUID
    user_id: uuid.UUID
    roadmap_id: uuid.UUID
    block_id: Optional[uuid.UUID] = None

    mode: SessionMode

    status: SessionStatus
    card_queue: List[uuid.UUID] = []
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
    roadmap_id: Optional[uuid.UUID] = None
    block_id: Optional[uuid.UUID] = None
    mode: Optional[SessionMode] = None
    status: Optional[SessionStatus] = None


class SessionResult(BaseModel):
    session_id: uuid.UUID
    user_id: uuid.UUID
    roadmap_id: uuid.UUID
    mode: SessionMode
    total_cards: int
    correct_answers: int
    incorrect_answers: int
    review_answers: int
    accuracy_percentage: float
    completed_at: datetime


class SubmitAnswerRequest(BaseModel):
    card_id: uuid.UUID
    answer: CardStatus
