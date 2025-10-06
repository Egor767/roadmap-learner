import os
from pydantic_settings import BaseSettings


class DbConfig(BaseSettings):
    prefix: str = os.getenv("DB_PREFIX", "postgresql+asyncpg")
    host: str = os.getenv("DB_HOST", "localhost")
    port: str = os.getenv("DB_PORT", "5432")
    username: str = os.getenv("DB_USERNAME", "postgres")
    password: str = os.getenv("DB_PASSWORD", "postgres")
    db_name: str = os.getenv("DB_NAME", "test_db")

    @property
    def url(self) -> str:
        return f"{self.prefix}://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"


db_config = DbConfig()

