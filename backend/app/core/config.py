import logging
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("config")

DEFAULT_JWT_SECRET_KEY = "change-this-to-a-long-random-secret-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "Insorts News"
    API_V1_PREFIX: str = "/api"

    DATABASE_URL: str = "postgresql+psycopg2://localhost:5432/insorts_news"

    JWT_SECRET_KEY: str = DEFAULT_JWT_SECRET_KEY
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:4173,capacitor://localhost,http://localhost"

    RSS_FETCH_INTERVAL_MINUTES: int = 15
    ARTICLE_RETENTION_DAYS: int = 3

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    loaded = Settings()
    if loaded.JWT_SECRET_KEY == DEFAULT_JWT_SECRET_KEY:
        logger.warning(
            "JWT_SECRET_KEY is still the default placeholder — every token this "
            "app issues can be forged by anyone with the source code. Set a real "
            "random secret in the environment before deploying."
        )
    return loaded


settings = get_settings()
