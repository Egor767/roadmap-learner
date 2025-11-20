from typing import Annotated, TYPE_CHECKING
from fastapi import Depends

# from .db import get_db_session
# from repositories import BlockRepository
# from services import BlockService, AccessService
#
# if TYPE_CHECKING:
#     from sqlalchemy.ext.asyncio import AsyncSession
#
#
# async def get_block_repository(
#     session: Annotated[
#         "AsyncSession",
#         Depends(get_db_session),
#     ],
# ) -> BlockRepository:
#     yield BlockRepository(session)
#
#
# async def get_block_service(
#     repo: Annotated[
#         BlockRepository,
#         Depends(get_block_repository),
#     ],
# ) -> BlockService:
#     yield BlockService(repo)
