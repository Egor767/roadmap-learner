from typing import TYPE_CHECKING
from app.schemas.block import BlockRead
from app.schemas.card import CardRead
from app.schemas.roadmap import RoadmapRead
from app.schemas.user import UserRead

if TYPE_CHECKING:
    from app.models import (
        Roadmap,
        User,
        Block,
        Card,
    )


async def user_orm_to_model(db_user: "User" | None) -> UserRead | None:
    if db_user:
        return UserRead.model_validate(db_user)
    return


async def roadmap_orm_to_model(db_roadmap: "Roadmap" | None) -> RoadmapRead | None:
    if db_roadmap:
        return RoadmapRead.model_validate(db_roadmap)
    return


def block_orm_to_model(db_block: "Block" | None) -> BlockRead | None:
    if db_block:
        return BlockRead.model_validate(db_block)
    return


def card_orm_to_model(db_card: "Card" | None) -> CardRead | None:
    if db_card:
        return CardRead.model_validate(db_card)
    return
