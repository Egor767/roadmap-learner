import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.api.v1 import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler('app.log')
    ],
)

app = FastAPI(title="RoadMap Learner API", version="1.0", lifespan=lifespan)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


app.include_router(main_router, prefix="/api/v1.0")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="localhost", port=8080, reload=True)
