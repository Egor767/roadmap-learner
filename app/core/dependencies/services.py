from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.clients import AIClient
from app.services import (
    AIService,
    BlockService,
    CardService,
    QuestionService,
    RoadmapService,
    SessionService,
    UserService,
)

from .cache import get_cache
from .clients import get_ai_client
from .repositories import (
    get_block_repository,
    get_card_progress_repository,
    get_card_repository,
    get_question_card_repository,
    get_question_progress_repository,
    get_question_repository,
    get_roadmap_repository,
    get_session_item_repository,
    get_session_repository,
    get_user_repository,
)

if TYPE_CHECKING:
    from cache import CacheHelper

    from app.repositories import (
        BlockRepository,
        CardRepository,
        QuestionCardRepository,
        QuestionRepository,
        RoadmapRepository,
        SessionItemRepository,
        SessionRepository,
        UserCardProgressRepository,
        UserQuestionProgressRepository,
        UserRepository,
    )


def get_user_service(
    user_repo: Annotated["UserRepository", Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repo)


def get_roadmap_service(
    repo: Annotated["RoadmapRepository", Depends(get_roadmap_repository)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> RoadmapService:
    return RoadmapService(repo, cache)


def get_block_service(
    repo: Annotated["BlockRepository", Depends(get_block_repository)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> BlockService:
    return BlockService(repo, cache)


def get_card_service(
    repo: Annotated["CardRepository", Depends(get_card_repository)],
    progress_repo: Annotated["UserCardProgressRepository", Depends(get_card_progress_repository)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> CardService:
    return CardService(repo, progress_repo, cache)


def get_question_service(
    repo: Annotated["QuestionRepository", Depends(get_question_repository)],
    progress_repo: Annotated["UserQuestionProgressRepository", Depends(get_question_progress_repository)],
    question_card_repo: Annotated["QuestionCardRepository", Depends(get_question_card_repository)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> QuestionService:
    return QuestionService(repo, progress_repo, question_card_repo, cache)


def get_ai_service(
    ai_client: Annotated["AIClient", Depends(get_ai_client)],
    roadmap_service: Annotated[RoadmapService, Depends(get_roadmap_service)],
    block_service: Annotated[BlockService, Depends(get_block_service)],
    question_service: Annotated[QuestionService, Depends(get_question_service)],
    card_service: Annotated[CardService, Depends(get_card_service)],
) -> AIService:
    return AIService(ai_client, roadmap_service, block_service, question_service, card_service)


def get_session_service(
    repo: Annotated["SessionRepository", Depends(get_session_repository)],
    block_repo: Annotated["BlockRepository", Depends(get_block_repository)],
    session_item_repo: Annotated["SessionItemRepository", Depends(get_session_item_repository)],
    question_repo: Annotated["QuestionRepository", Depends(get_question_repository)],
    card_repo: Annotated["CardRepository", Depends(get_card_repository)],
    question_progress_repo: Annotated["UserQuestionProgressRepository", Depends(get_question_progress_repository)],
    ai_client: Annotated["AIClient", Depends(get_ai_client)],
    cache: Annotated["CacheHelper", Depends(get_cache)],
) -> SessionService:
    return SessionService(
        repo, block_repo, question_repo, card_repo, session_item_repo, question_progress_repo, ai_client, cache
    )
