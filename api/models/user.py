from datetime import datetime, timezone

from beanie import Document, Indexed
from pydantic import EmailStr, Field


class User(Document):
    name: str = Field(min_length=1, max_length=255)
    email: Indexed(EmailStr, unique=True)  # type: ignore[valid-type]
    password: str
    profile_picture: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
