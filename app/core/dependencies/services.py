from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from app.services import (
    UserService,
    RoadmapService,
    BlockService,
    CardService,
    SessionService,
)
from .repositories import (
    get_user_repository,
    get_roadmap_repository,
    get_block_repository,
    get_card_repository,
    get_session_repository,
)

from .cache import get_cache

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from cache import CacheHelper
    from repositories import (
        UserRepository,
        RoadmapRepository,
        BlockRepository,
        CardRepository,
        SessionRepository,
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
    redis: Annotated[
        "Redis",
        Depends(get_cache),
    ],
) -> BlockService:
    return BlockService(
        repo,
        redis,
    )


def get_card_service(
    repo: Annotated[
        "CardRepository",
        Depends(get_card_repository),
    ],
    redis: Annotated[
        "Redis",
        Depends(get_cache),
    ],
) -> CardService:
    return CardService(
        repo,
        redis,
    )


def get_session_service(
    repo: Annotated[
        "SessionRepository",
        Depends(get_session_repository),
    ],
    redis: Annotated[
        "Redis",
        Depends(get_cache),
    ],
) -> SessionService:
    return SessionService(
        repo,
        redis,
    )
