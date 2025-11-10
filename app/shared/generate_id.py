import uuid

from app.core.types import BaseIDType


async def generate_base_id() -> BaseIDType:
    return uuid.uuid4()
