import uuid

from core.types import BaseIdType


async def generate_base_id() -> BaseIdType:
    return uuid.uuid4()
