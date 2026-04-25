from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Finora API"
    APP_VERSION: str = "2.0.0"
    CLIENT_URL: str = "http://localhost:3000"
    API_BASE_PATH: str = "/api"

    MONGODB_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "finora"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    GOOGLE_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    CLOUDINARY_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None
    SMTP_FROM: str = "no-reply@finora.app"
    SMTP_PORT: int = 587

    CHROMA_PERSIST_DIR: str = "./api/chroma_db"
    ENABLE_SCHEDULER: bool = False
    COOKIE_NAME: str = "access_token"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
