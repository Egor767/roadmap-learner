from pydantic_settings import BaseSettings
from pydantic import BaseModel


class DBSettings(BaseModel):
    host: str = "localhost"
    port: str = "5433"
    username: str = "postgres"
    password: str = "postgres"
    name: str = "roadmap"
    echo: bool = False

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

    class Config:
        env_file = ".env"


class Settings(BaseSettings):
    db: DBSettings = DBSettings()


settings = Settings()
