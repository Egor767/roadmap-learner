from typing import List

from fastapi import HTTPException

from app.core.handlers import service_handler
from app.core.logging import session_manager_service_logger as logger
from app.core.types import BaseIDType
from app.external.card_service import get_card_from_service
from app.external.session_manager_service import calculate_session_stats
from app.repositories.session_manager import SessionManagerRepository
from app.schemas.card import CardResponse
from app.schemas.session_manager import (
    SessionResponse,
    SessionCreate,
    SessionFilters,
    SessionResult,
    SubmitAnswerRequest,
)
from shared.generate_id import generate_base_id


class SessionManagerService:
    def __init__(self, repo: SessionManagerRepository):
        self.repo = repo

    @service_handler
    async def get_all_sessions(self) -> List[SessionResponse]:
        sessions = await self.repo.get_all_sessions()
        validated_sessions = [
            SessionResponse.model_validate(session) for session in sessions
        ]
        logger.info(f"Successful get all sessions, count: {len(validated_sessions)}")
        return validated_sessions

    @service_handler
    async def get_user_session(
        self, user_id: BaseIDType, session_id: BaseIDType
    ) -> SessionResponse:
        session = await self.repo.get_user_session(user_id, session_id)
        if not session:
            logger.warning(f"Session not found or access denied")
            raise ValueError("Session not found or access denied")
        logger.info(f"Successful get user session")
        return SessionResponse.model_validate(session)

    @service_handler
    async def get_user_sessions(
        self, user_id: BaseIDType, filters: SessionFilters
    ) -> List[SessionResponse]:
        sessions = await self.repo.get_user_sessions(user_id, filters)
        validated_sessions = [
            SessionResponse.model_validate(session) for session in sessions
        ]
        logger.info(
            f"Retrieved {len(validated_sessions)} sessions with filters: {filters}"
        )
        return validated_sessions

    @service_handler
    async def create_session(
        self, user_id: BaseIDType, session_create_data: SessionCreate
    ) -> SessionResponse:
        # need to check here if existing

        session_data = session_create_data.model_dump()
        del session_data["settings"]
        session_data["user_id"] = user_id
        session_data["id"] = generate_base_id()

        logger.info(
            f"Creating new session: {session_create_data.mode} for user: {user_id}"
        )
        created_session = await self.repo.create_session(user_id, session_data)

        logger.info(f"Session created successfully: {created_session.session_id}")
        return SessionResponse.model_validate(created_session)

    @service_handler
    async def finish_session(
        self, user_id: BaseIDType, session_id: BaseIDType
    ) -> SessionResult:
        finished_session = await self.repo.finish_session(user_id, session_id)

        if not finished_session:
            logger.warning(f"Session not found for finish: {session_id}")
            raise ValueError("Session not found")

        result_data = {
            **finished_session.model_dump(),
            **calculate_session_stats(finished_session),
        }

        logger.info(f"Successful finishing session: {session_id}")
        return SessionResult.model_validate(result_data)

    @service_handler
    async def abandon_session(
        self, user_id: BaseIDType, session_id: BaseIDType
    ) -> bool:
        success = await self.repo.abandon_session(user_id, session_id)

        if success:
            logger.info(f"Session abandoned successfully: {session_id}")
        else:
            logger.warning(
                f"Failed to abandon session: {session_id} - session not found, not active, or not owned by user"
            )

        return success

    @service_handler
    async def get_next_card(
        self, user_id: BaseIDType, session_id: BaseIDType
    ) -> CardResponse:
        next_card_id = await self.repo.get_next_card_id(user_id, session_id)

        if not next_card_id:
            logger.warning(f"Next card not found for session: {session_id}")
            raise ValueError("Next card not found")

        logger.info(f"Successfully retrieved next card_id for session: {session_id}")

        card_data = await get_card_from_service(str(user_id), str(next_card_id))
        if not card_data:
            raise HTTPException(status_code=404, detail="Card not found")

        return CardResponse.model_validate(card_data)

    @service_handler
    async def submit_answer(
        self,
        user_id: BaseIDType,
        session_id: BaseIDType,
        answer_data: SubmitAnswerRequest,
    ) -> SessionResponse:
        # need ro check if session exist, status==active, if mode==exam then answer_data.answer!=review
        # answer_data.card_id in Session.card_queue

        updated_session = await self.repo.submit_answer(
            user_id, session_id, answer_data
        )

        if not updated_session:
            logger.warning(f"Failed to update session: {session_id}")
            raise ValueError("Failed to update session")

        logger.info(f"Successfully submitted answer for session: {session_id}")
        return SessionResponse.model_validate(updated_session)

    @service_handler
    async def delete_session(self, user_id: BaseIDType, session_id: BaseIDType) -> bool:
        # check roots

        success = await self.repo.delete_session(user_id, session_id)
        if success:
            logger.info(f"Session deleted successfully: {session_id}")
        else:
            logger.warning(f"Session not found for deletion: {session_id}")
        return success
