import os
from pydantic_settings import BaseSettings


class DbConfig(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: str = "5433"
    DB_USERNAME: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "roadmap"
    echo: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


db_config = DbConfig()
