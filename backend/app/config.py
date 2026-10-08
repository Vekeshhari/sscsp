import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./sscsp.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "change_me")
    jwt_alg: str = "HS256"
    access_token_minutes: int = 30
    block_cvss: float = float(os.getenv("BLOCK_CVSS", "7.0"))


settings = Settings()
