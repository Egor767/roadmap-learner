import uvicorn
from fastapi import FastAPI
from app.api.v1 import router


def create_app() -> FastAPI:
    app = FastAPI(title="RoadMap Learner API", version="1.0")
    app.include_router(router, prefix="/api/v1.0")
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app="app.main:app",
        host="localhost",
        port=8080,
        reload=True
    )

