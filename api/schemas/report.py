from datetime import datetime

from pydantic import BaseModel

from api.models.report import ReportStatus
from api.schemas.user import ReportSettingResponse


class UpdateReportSettingInput(BaseModel):
    isEnabled: bool | None = None


class ReportHistoryItem(BaseModel):
    id: str
    period: str
    sentDate: datetime
    status: ReportStatus
    createdAt: datetime
    updatedAt: datetime


class ReportGenerateSummaryItem(BaseModel):
    name: str
    amount: float
    percent: int


class ReportGenerateResponse(BaseModel):
    message: str
    period: str | None = None
    summary: dict | None = None
    insights: list[str] | list[dict] | None = None


class ReportListResponse(BaseModel):
    message: str
    reports: list[ReportHistoryItem]
    pagination: dict
    reportSetting: ReportSettingResponse | None = None
