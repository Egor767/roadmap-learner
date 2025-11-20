# from typing import Annotated, TYPE_CHECKING
# from fastapi import Depends
#
# from .db import get_db_session
# from repositories import SessionManagerRepository
# from services import SessionManagerService
#
# if TYPE_CHECKING:
#     from sqlalchemy.ext.asyncio import AsyncSession
#
#
# async def get_session_manager_repository(
#     session: Annotated[
#         "AsyncSession",
#         Depends(get_db_session),
#     ],
# ) -> SessionManagerRepository:
#     yield SessionManagerRepository(session)
#
#
# async def get_session_manager_service(
#     repo: Annotated[
#         SessionManagerRepository,
#         Depends(get_session_manager_repository),
#     ],
# ) -> SessionManagerService:
#     yield SessionManagerService(repo)
