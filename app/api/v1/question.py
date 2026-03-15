from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.core.authentication.fastapi_users import current_active_user
from app.core.config import settings
from app.core.custom_types import BaseIdType
from app.core.dependencies.services import get_question_service
from app.core.handlers import router_handler
from app.schemas.question import (
    QuestionConfirmRequest,
    QuestionCreate,
    QuestionFilters,
    QuestionMove,
    QuestionRead,
    QuestionUpdate,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services import QuestionService


router = APIRouter(
    prefix=settings.api.v1.questions,
    tags=["Questions"],
)


@router.get(
    "",
    name="questions:all_questions",
    response_model=list[QuestionRead],
)
@router_handler
async def get_all_questions(
    question_service: Annotated[
        "QuestionService",
        Depends(get_question_service),
    ],
) -> list[QuestionRead]:
    return await question_service.get_all()


# -------------------------------------- GET ----------------------------------------------
@router.get(
    "/filters",
    name="questions:filter_questions",
    response_model=list[QuestionRead],
)
@router_handler
async def get_questions(
    filters: Annotated[
        QuestionFilters,
        Depends(),
    ],
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    question_service: Annotated[
        "QuestionService",
        Depends(get_question_service),
    ],
    block_filter: Annotated[list[BaseIdType] | None, Query()] = None,
) -> list[QuestionRead]:
    return await question_service.get_by_filters(
        current_user,
        filters,
        block_filter,
    )


@router.get(
    "/{question_id}",
    name="questions:question",
    response_model=QuestionRead,
)
@router_handler
async def get_question(
    question_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    question_service: Annotated[
        "QuestionService",
        Depends(get_question_service),
    ],
) -> QuestionRead:
    return await question_service.get_by_id(
        current_user,
        question_id,
    )


# -------------------------------------- CREATE --------------------------------------
@router.post(
    "",
    name="questions:create_question",
    response_model=QuestionRead,
)
@router_handler
async def create_question(
    question_create_data: QuestionCreate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    question_service: Annotated[
        "QuestionService",
        Depends(get_question_service),
    ],
) -> QuestionRead:
    return await question_service.create(
        current_user,
        question_create_data,
    )


@router.post(
    "/batch",
    name="questions:create_batch_questions",
    response_model=list[QuestionRead],
    status_code=status.HTTP_201_CREATED,
)
@router_handler
async def confirm_questions(
    body: QuestionConfirmRequest,
    current_user: Annotated["User", Depends(current_active_user)],
    question_service: Annotated["QuestionService", Depends(get_question_service)],
) -> list[QuestionRead]:
    return await question_service.create_multiple(current_user, body)


# -------------------------------------- DELETE --------------------------------------
@router.delete(
    "/{question_id}",
    name="questions:delete_question",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router_handler
async def delete_question(
    question_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    question_service: Annotated[
        "QuestionService",
        Depends(get_question_service),
    ],
) -> None:
    await question_service.delete(
        current_user,
        question_id,
    )


# -------------------------------------- UPDATE --------------------------------------
@router.patch(
    "/{question_id}",
    name="questions:patch_question",
    response_model=QuestionRead,
)
@router_handler
async def update_question(
    question_id: BaseIdType,
    question_update_data: QuestionUpdate,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    question_service: Annotated[
        "QuestionService",
        Depends(get_question_service),
    ],
) -> QuestionRead:
    return await question_service.update(
        current_user,
        question_id,
        question_update_data,
    )


@router.patch(
    "/{question_id}/move",
    name="questions:move_question",
    response_model=QuestionRead,
)
@router_handler
async def move_question(
    question_id: BaseIdType,
    move_data: QuestionMove,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    question_service: Annotated[
        "QuestionService",
        Depends(get_question_service),
    ],
) -> QuestionRead:
    return await question_service.move(
        current_user,
        question_id,
        move_data,
    )


@router.post(
    "/{question_id}/link-card",
    name="questions:link_card",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router_handler
async def link_card(
    question_id: BaseIdType,
    card_id: BaseIdType,
    current_user: Annotated[
        "User",
        Depends(current_active_user),
    ],
    question_service: Annotated[
        "QuestionService",
        Depends(get_question_service),
    ],
):
    await question_service.link_card(
        current_user,
        question_id,
        card_id,
    )
