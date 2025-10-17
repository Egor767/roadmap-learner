from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime
from typing import Optional


class RoadMapCreate(BaseModel):
    user_id: uuid.UUID
    title: str
    description: Optional[str] = None


class RoadMapUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class RoadMapInDB(BaseModel):
    road_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoadMapResponse(RoadMapInDB):
    pass
