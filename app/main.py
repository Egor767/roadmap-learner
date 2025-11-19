import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from api import router as api_router
from core.config import settings


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

app = FastAPI(
    title="Roadmap Learner API",
    version="1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/hello")
async def hello():
    return "Hello!"


app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
