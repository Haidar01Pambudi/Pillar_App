from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_fil=".env", env_prefix="PILLAR_", extra="ignore")

    app_name: str = "Pillar Distribution"
    database_url: str = "postgresql+psycopg://pillar:pillar@localhost:5000/pillar"
    secret_key: str = "change-me"
    sesson_max_age: int = 60*60*10
    https_only_cookies: bool = False
    timezone: str = "Asia/Jakarta"

    enable_modules: list[str] = [
        "dashboard",
        "distribution",
        "issues",
        "releases",
        "lookups",
        "admin",
    ]

    page_size: int = 50

@lru_cache
def get_settings() -> Settings:
    return Settings()