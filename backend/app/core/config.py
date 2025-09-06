from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    app_env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str

    jwt_secret: str
    jwt_alg: str = "HS256"
    jwt_access_ttl_min: int = 15
    jwt_refresh_ttl_days: int = 7

    password_hash_scheme: str = "argon2"

    cors_origins: List[str] = []

    rate_limit_per_min: int = 60
    rate_limit_burst: int = 120
    redis_url: str | None = None

    risk_free_rate_annual: float = 0.03
    default_benchmark: str = "SPY"

    class Config:
        env_file = ".env"

    def __init__(self, **values):
        super().__init__(**values)
        cors = os.getenv("CORS_ORIGINS", "")
        if cors:
            self.cors_origins = [o.strip() for o in cors.split(",") if o.strip()]

settings = Settings()