import uuid
from typing import List

from app.core.handlers import service_handler
from app.core.logging import session_manager_service_logger as logger
from app.repositories.session_manager.interface import ISessionManagerRepository
from app.schemas.card import CardResponse, CardStatus
from app.schemas.session_manager import SessionResponse, SessionUpdate, SessionCreate, SessionFilters, SessionResult


class SessionManagerService:
    def __init__(self, repo: ISessionManagerRepository):
        self.repo = repo

    @service_handler
    async def get_all_sessions(self) -> List[SessionResponse]:
        sessions = await self.repo.get_all_sessions()
        validated_sessions = [SessionResponse.model_validate(session) for session in sessions]
        logger.info(f"Successful get all sessions, count: {len(validated_sessions)}")
        return validated_sessions

    @service_handler
    async def get_user_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> SessionResponse:
        session = await self.repo.get_user_session(user_id, session_id)
        if not session:
            logger.warning(f"Session not found or access denied")
            raise ValueError("Session not found or access denied")
        logger.info(f"Successful get user session")
        return SessionResponse.model_validate(session)

    @service_handler
    async def get_user_sessions(self, user_id: uuid.UUID, filters: SessionFilters) -> List[SessionResponse]:
        sessions = await self.repo.get_user_sessions(user_id, filters)
        validated_sessions = [SessionResponse.model_validate(session) for session in sessions]
        logger.info(f"Retrieved {len(validated_sessions)} sessions with filters: {filters}")
        return validated_sessions

    @service_handler
    async def create_session(self, user_id: uuid.UUID, session_create_data: SessionCreate) -> SessionResponse:
        # need to check here if existing

        session_data = session_create_data.model_dump()
        # пока так
        del session_data["settings"]
        session_data["user_id"] = user_id
        session_data["session_id"] = uuid.uuid4()

        logger.info(f"Creating new session: {session_create_data.mode} for user: {user_id}")
        created_session = await self.repo.create_session(session_data)

        logger.info(f"Session created successfully: {created_session.session_id}")
        return SessionResponse.model_validate(created_session)

    @service_handler
    async def finish_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> SessionResult:
        ...

    @service_handler
    async def abandon_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> bool:
        ...

    @service_handler
    async def get_next_card(self, user_id: uuid.UUID, session_id: uuid.UUID, limit: int) -> CardResponse:
        ...

    @service_handler
    async def submit_answer(self, user_id: uuid.UUID, session_id: uuid.UUID, card_id: uuid.UUID,
                            answer: CardStatus) -> SessionResponse:
        ...

