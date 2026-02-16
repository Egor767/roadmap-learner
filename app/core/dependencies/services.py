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

from .cache import get_redis

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from repositories import (
        UserRepository,
        RoadmapRepository,
        BlockRepository,
        CardRepository,
        SessionRepository,
    )


async def get_user_service(
    user_repo: Annotated[
        "UserRepository",
        Depends(get_user_repository),
    ],
) -> UserService:
    yield UserService(user_repo)


async def get_roadmap_service(
    repo: Annotated[
        "RoadmapRepository",
        Depends(get_roadmap_repository),
    ],
    redis: Annotated[
        "Redis",
        Depends(get_redis),
    ],
) -> RoadmapService:
    yield RoadmapService(
        repo,
        redis,
    )


async def get_block_service(
    repo: Annotated[
        "BlockRepository",
        Depends(get_block_repository),
    ],
    redis: Annotated[
        "Redis",
        Depends(get_redis),
    ],
) -> BlockService:
    yield BlockService(
        repo,
        redis,
    )


async def get_card_service(
    repo: Annotated[
        "CardRepository",
        Depends(get_card_repository),
    ],
    redis: Annotated[
        "Redis",
        Depends(get_redis),
    ],
) -> CardService:
    yield CardService(
        repo,
        redis,
    )


async def get_session_service(
    repo: Annotated[
        "SessionRepository",
        Depends(get_session_repository),
    ],
    redis: Annotated[
        "Redis",
        Depends(get_redis),
    ],
) -> SessionService:
    yield SessionService(
        repo,
        redis,
    )
