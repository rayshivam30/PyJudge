from functools import lru_cache
from pathlib import Path
import tempfile

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PyJudge"
    database_url: str = f"sqlite:///{Path(tempfile.gettempdir()).as_posix()}/pyjudge.db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    executor_use_docker: bool = False
    executor_workspace_root: str = "/tmp/pyjudge"
    force_inline_judge: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
