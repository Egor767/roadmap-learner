# from typing import Annotated, TYPE_CHECKING
# from fastapi import Depends
#
# from .access import get_access_service
# from .db import get_db_session
# from repositories import RoadmapRepository
#
# if TYPE_CHECKING:
#     from services import AccessService
#     from sqlalchemy.ext.asyncio import AsyncSession
#     from services import RoadmapService
#
#
# async def get_roadmap_repository(
#     session: Annotated[
#         "AsyncSession",
#         Depends(get_db_session),
#     ],
# ) -> RoadmapRepository:
#     yield RoadmapRepository(session)
#
#
# async def get_roadmap_service(
#     repo: Annotated[
#         "RoadmapRepository",
#         Depends(get_roadmap_repository),
#     ],
#     access_service: Annotated[
#         "AccessService",
#         Depends(get_access_service),
#     ],
# ) -> "RoadmapService":
#     from services.roadmap import RoadmapService
#
#     yield RoadmapService(repo, access_service)
