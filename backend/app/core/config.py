"""Application settings loaded from environment variables."""

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration shared by the API and database tooling."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "SalesIA Enterprise"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://salesia:salesia@localhost:5432/salesia"
    database_ssl_mode: str = "prefer"
    database_pool_size: int = Field(default=5, ge=1, le=20)
    database_max_overflow: int = Field(default=5, ge=0, le=20)
    database_pool_recycle_seconds: int = Field(default=300, ge=30)
    secret_key: SecretStr = SecretStr("replace-with-a-random-secret")
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    jwt_algorithm: Literal["HS256"] = "HS256"
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"
    timezone: str = "America/Lima"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        """Make provider-style PostgreSQL URLs explicit for psycopg 3."""

        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("database_ssl_mode")
    @classmethod
    def validate_ssl_mode(cls, value: str) -> str:
        allowed = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
        if value not in allowed:
            raise ValueError(f"DATABASE_SSL_MODE debe ser uno de: {', '.join(sorted(allowed))}")
        return value

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "test", "production"}
        if value not in allowed:
            raise ValueError(f"ENVIRONMENT debe ser uno de: {', '.join(sorted(allowed))}")
        return value

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        normalized = value.upper()
        if normalized not in allowed:
            raise ValueError(f"LOG_LEVEL debe ser uno de: {', '.join(sorted(allowed))}")
        return normalized

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        secret = self.secret_key.get_secret_value()
        if secret == "replace-with-a-random-secret" or len(secret) < 32:
            raise ValueError("SECRET_KEY debe ser aleatoria y tener al menos 32 caracteres")
        if self.environment == "production" and "*" in self.cors_origin_list:
            raise ValueError("CORS_ORIGINS no puede contener * en produccion")
        return self

    @property
    def database_connect_args(self) -> dict[str, str]:
        return {"sslmode": self.database_ssl_mode}

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
