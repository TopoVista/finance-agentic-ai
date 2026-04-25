from datetime import datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field


class ReportStatus(str, Enum):
    SENT = "SENT"
    PENDING = "PENDING"
    FAILED = "FAILED"
    NO_ACTIVITY = "NO_ACTIVITY"


class Report(Document):
    user_id: Indexed(str)  # type: ignore[valid-type]
    period: str
    sent_date: datetime
    status: ReportStatus = ReportStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "reports"

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
