from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api.core.config import settings
from api.models.report import Report, ReportStatus
from api.models.report_setting import ReportSetting

scheduler = AsyncIOScheduler(timezone="UTC")


async def monthly_report_job() -> None:
    due_settings = await ReportSetting.find(
        ReportSetting.is_enabled == True,  # noqa: E712
        ReportSetting.next_report_date <= datetime.now(timezone.utc),
    ).to_list()
    for setting in due_settings:
        await Report(
            user_id=setting.user_id,
            period=setting.next_report_date.strftime("%B %Y") if setting.next_report_date else "Scheduled",
            sent_date=datetime.now(timezone.utc),
            status=ReportStatus.PENDING,
        ).insert()


def start_scheduler() -> None:
    if not settings.ENABLE_SCHEDULER or scheduler.running:
        return
    scheduler.add_job(monthly_report_job, "cron", day=1, hour=0, minute=5, id="monthly-report-job")
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
