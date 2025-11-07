from pydantic_settings import BaseSettings
from pydantic import BaseModel


class DBSettings(BaseModel):
    host: str = "localhost"
    port: str = "5433"
    username: str = "postgres"
    password: str = "postgres"
    name: str = "roadmap"
    echo: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

    class Config:
        env_file = ".env"


class Settings(BaseSettings):
    db: DBSettings = DBSettings()


settings = Settings()
