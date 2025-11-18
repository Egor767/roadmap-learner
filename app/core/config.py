from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class DBConfig(BaseModel):
    host: str = "localhost"
    port: str = "5433"
    username: str = "postgres"
    password: str = "postgres"
    name: str = "roadmap"
    echo: bool = False
    url_prefix: str = "postgresql+asyncpg"

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> str:
        return f"{self.url_prefix}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8080


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"
    roadmaps: str = "/roadmaps"
    blocks: str = "/roadmaps/{roadmap_id}/blocks"
    blocks_resource: str = "/blocks"
    cards: str = "/roadmaps/{roadmap_id}/blocks/{block_id}/cards"
    cards_resource: str = "/cards"
    sessions: str = "/sessions"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        parts = (self.prefix, self.v1.prefix, self.v1.auth, "/login")
        path = "".join(parts)
        return path.removeprefix("/")


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    db: DBConfig
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    access_token: AccessToken


settings = Settings()
