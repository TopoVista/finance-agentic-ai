from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from api.models.report_setting import ReportFrequency


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    profilePicture: str | None = None
    createdAt: datetime
    updatedAt: datetime


class UserUpdateInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ReportSettingResponse(BaseModel):
    id: str
    frequency: ReportFrequency
    isEnabled: bool
    nextReportDate: datetime | None = None
    lastSentDate: datetime | None = None
