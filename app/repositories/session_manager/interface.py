import uuid
from abc import ABC, abstractmethod
from typing import List

from app.schemas.card import CardResponse, CardStatus
from app.schemas.session_manager import SessionInDB, SessionResponse, SessionFilters, SessionCreate, SessionUpdate, \
    SessionResult


class ISessionManagerRepository(ABC):
    @abstractmethod
    async def get_all_sessions(self) -> List[SessionInDB]:
        ...

    @abstractmethod
    async def get_user_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> SessionInDB: ...

    @abstractmethod
    async def get_user_sessions(self, user_id: uuid.UUID, filters: SessionFilters) -> List[SessionInDB]: ...

    @abstractmethod
    async def create_session(self, user_id: uuid.UUID, session_create_data: SessionCreate) -> SessionInDB: ...

    @abstractmethod
    async def finish_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> SessionResult: ...

    @abstractmethod
    async def abandon_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> bool: ...

    @abstractmethod
    async def get_next_card(self, user_id: uuid.UUID, session_id: uuid.UUID, limit: int) -> CardResponse: ...

    @abstractmethod
    async def submit_answer(self, user_id: uuid.UUID, session_id: uuid.UUID, card_id: uuid.UUID, answer: CardStatus) -> SessionResponse: ...

