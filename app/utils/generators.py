import uuid
from typing import Optional

from app.core.types import BaseIdType


def id_generator() -> Optional[BaseIdType]:
    if issubclass(BaseIdType, uuid.UUID):
        return uuid.uuid4()
    return


def server_id_generator() -> str:
    if issubclass(BaseIdType, uuid.UUID):
        return "gen_random_uuid()"
    return ""
