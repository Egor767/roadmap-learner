# from typing import Annotated, TYPE_CHECKING
# from fastapi import Depends
#
# # from services import AccessService
# from .roadmaps import get_roadmap_repository
#
# if TYPE_CHECKING:
#     from services import AccessService
#     from repositories import RoadmapRepository
#
#
# async def get_access_service(
#     roadmap_repo: Annotated[
#         "RoadmapRepository",
#         Depends(get_roadmap_repository),
#     ],
# ) -> "AccessService":
#     from services import AccessService
#
#     yield AccessService(roadmap_repo)
