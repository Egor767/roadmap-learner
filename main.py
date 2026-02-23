import logging
from contextlib import asynccontextmanager

import uvicorn
from app.api import router as api_router
from app.core.cache.helper import CacheHelper
from app.core.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cache = CacheHelper(settings.redis.url)
    yield
    await app.state.cache.close()


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

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def hello():
    return {"status": "active"}


app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
