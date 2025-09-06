from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # v2 config (replaces inner Config)
    model_config = SettingsConfigDict(
        env_file=".env",          # used locally; Railway injects real env vars
        env_prefix="",            # no prefix; matches Railway's names
        case_sensitive=False,
    )

    app_env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str            # Railway Postgres usually exposes DATABASE_URL
    jwt_secret: str
    jwt_alg: str = "HS256"
    jwt_access_ttl_min: int = 15
    jwt_refresh_ttl_days: int = 7

    password_hash_scheme: str = "argon2"

    # Read from CORS_ORIGINS env; parse CSV into a list
    cors_origins: List[str] = Field(default_factory=list, alias="CORS_ORIGINS")

    rate_limit_per_min: int = 60
    rate_limit_burst: int = 120
    redis_url: Optional[str] = None  # Railway Redis usually exposes REDIS_URL

    risk_free_rate_annual: float = 0.03
    default_benchmark: str = "SPY"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
