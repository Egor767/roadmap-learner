from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/create")
async def create_user():
    ...

