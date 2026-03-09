from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.services import (
    BlockService,
    CardService,
    QuestionService,
    RoadmapService,
    SessionService,
    UserService,
)

from .cache import get_cache
from .repositories import (
    get_block_repository,
    get_card_repository,
    get_question_progress_repository,
    get_question_repository,
    get_roadmap_repository,
    get_session_repository,
    get_user_repository,
)

if TYPE_CHECKING:
    from cache import CacheHelper

    from repositories import (
        BlockRepository,
        CardRepository,
        QuestionRepository,
        RoadmapRepository,
        SessionRepository,
        UserQuestionProgressRepository,
        UserRepository,
    )


def get_user_service(
    user_repo: Annotated[
        "UserRepository",
        Depends(get_user_repository),
    ],
) -> UserService:
    return UserService(user_repo)


def get_roadmap_service(
    repo: Annotated[
        "RoadmapRepository",
        Depends(get_roadmap_repository),
    ],
    cache: Annotated[
        "CacheHelper",
        Depends(get_cache),
    ],
) -> RoadmapService:
    return RoadmapService(
        repo,
        cache,
    )


def get_block_service(
    repo: Annotated[
        "BlockRepository",
        Depends(get_block_repository),
    ],
    cache: Annotated[
        "CacheHelper",
        Depends(get_cache),
    ],
) -> BlockService:
    return BlockService(
        repo,
        cache,
    )


def get_card_service(
    repo: Annotated[
        "CardRepository",
        Depends(get_card_repository),
    ],
    cache: Annotated[
        "CacheHelper",
        Depends(get_cache),
    ],
) -> CardService:
    return CardService(
        repo,
        cache,
    )


def get_question_service(
    repo: Annotated[
        "QuestionRepository",
        Depends(get_question_repository),
    ],
    progress_repo: Annotated[
        "UserQuestionProgressRepository",
        Depends(get_question_progress_repository),
    ],
    cache: Annotated[
        "CacheHelper",
        Depends(get_cache),
    ],
) -> QuestionService:
    return QuestionService(
        repo,
        progress_repo,
        cache,
    )


def get_session_service(
    repo: Annotated[
        "SessionRepository",
        Depends(get_session_repository),
    ],
    cache: Annotated[
        "CacheHelper",
        Depends(get_cache),
    ],
) -> SessionService:
    return SessionService(
        repo,
        cache,
    )
