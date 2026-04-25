from datetime import datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field


class ReportFrequency(str, Enum):
    MONTHLY = "MONTHLY"


class ReportSetting(Document):
    user_id: Indexed(str, unique=True)  # type: ignore[valid-type]
    frequency: ReportFrequency = ReportFrequency.MONTHLY
    is_enabled: bool = True
    next_report_date: datetime | None = None
    last_sent_date: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "report_settings"

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
