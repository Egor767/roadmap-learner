from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.dependencies.services import (
    get_load_service,
)
from app.core.handlers import router_handler
from app.schemas.block import BlockRead
from app.schemas.load import (
    BlockConfirmRequest,
    BlockDistributeRequest,
    BlockDistributeResponse,
    QuestionConfirmRequest,
    QuestionDistributeRequest,
    QuestionDistributeResponse,
)
from app.schemas.question import QuestionRead

if TYPE_CHECKING:
    from app.models import User
    from app.services.load import LoadService


router = APIRouter(
    prefix=settings.api.v1.load,
    tags=["Load"],
)


@router.post(
    "/blocks/distribute",
    name="load:distribute_blocks",
    response_model=BlockDistributeResponse,
    status_code=status.HTTP_200_OK,
)
@router_handler
async def distribute_blocks(
    request: BlockDistributeRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    load_service: Annotated["LoadService", Depends(get_load_service)],
) -> BlockDistributeResponse:
    return await load_service.distribute_blocks(
        current_user,
        request,
    )


@router.post(
    "/blocks/confirm",
    name="load:confirm_blocks",
    response_model=list[BlockRead],
    status_code=status.HTTP_201_CREATED,
)
@router_handler
async def confirm_blocks(
    body: BlockConfirmRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    load_service: Annotated["LoadService", Depends(get_load_service)],
) -> list[BlockRead]:
    return await load_service.confirm_blocks(current_user, body)


@router.post(
    "/questions/distribute",
    name="load:distribute_questions",
    response_model=QuestionDistributeResponse,
    status_code=status.HTTP_200_OK,
)
@router_handler
async def distribute_questions(
    request: QuestionDistributeRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    load_service: Annotated["LoadService", Depends(get_load_service)],
) -> QuestionDistributeResponse:
    return await load_service.distribute_questions(
        current_user,
        request,
    )


@router.post(
    "/questions/confirm",
    name="load:confirm_questions",
    response_model=list[QuestionRead],
    status_code=status.HTTP_201_CREATED,
)
@router_handler
async def confirm_questions(
    body: QuestionConfirmRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    load_service: Annotated["LoadService", Depends(get_load_service)],
) -> list[QuestionRead]:
    return await load_service.confirm_questions(current_user, body)
