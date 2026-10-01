"""Application settings loaded from environment variables."""

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    app_name: str = getenv("APP_NAME", "SalesIA Enterprise")
    environment: str = getenv("ENVIRONMENT", "development")
    api_v1_prefix: str = "/api/v1"


settings = Settings()
