from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from services import AccessService, RoadmapService
from services import BlockService, CardService, SessionManagerService, UserService
from .repositories import (
    get_block_repository,
    get_card_repository,
    get_session_manager_repository,
    get_roadmap_repository,
    get_user_repository,
)

if TYPE_CHECKING:
    from repositories import (
        RoadmapRepository,
        CardRepository,
        SessionManagerRepository,
        UserRepository,
    )
    from repositories import BlockRepository


async def get_user_service(
    user_repo: Annotated[
        "UserRepository",
        Depends(get_user_repository),
    ],
) -> UserService:
    yield UserService(user_repo)


async def get_access_service(
    roadmap_repo: Annotated[
        "RoadmapRepository",
        Depends(get_roadmap_repository),
    ],
) -> AccessService:
    yield AccessService(roadmap_repo)


async def get_roadmap_service(
    repo: Annotated[
        "RoadmapRepository",
        Depends(get_roadmap_repository),
    ],
    access_service: Annotated[
        "AccessService",
        Depends(get_access_service),
    ],
) -> RoadmapService:
    yield RoadmapService(repo, access_service)


async def get_block_service(
    repo: Annotated[
        "BlockRepository",
        Depends(get_block_repository),
    ],
    access_service: Annotated[
        "AccessService",
        Depends(get_access_service),
    ],
) -> BlockService:
    yield BlockService(repo, access_service)


async def get_card_service(
    repo: Annotated[
        "CardRepository",
        Depends(get_card_repository),
    ],
) -> CardService:
    yield CardService(repo)


async def get_session_manager_service(
    repo: Annotated[
        "SessionManagerRepository",
        Depends(get_session_manager_repository),
    ],
) -> SessionManagerService:
    yield SessionManagerService(repo)
