from datetime import datetime, timedelta, timezone

from api.models.report_setting import ReportFrequency
from api.models.transaction import RecurringInterval


def calculate_next_occurrence(date: datetime, recurring_interval: RecurringInterval) -> datetime:
    base = date.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    if recurring_interval == RecurringInterval.DAILY:
        return base + timedelta(days=1)
    if recurring_interval == RecurringInterval.WEEKLY:
        return base + timedelta(weeks=1)
    if recurring_interval == RecurringInterval.MONTHLY:
        return base + timedelta(days=30)
    return base + timedelta(days=365)


def calculate_next_report_date(last_sent_date: datetime | None = None, frequency: ReportFrequency = ReportFrequency.MONTHLY) -> datetime:
    _ = frequency
    anchor = (last_sent_date or datetime.now(timezone.utc)).astimezone(timezone.utc)
    next_month = (anchor.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)).replace(day=1)
    return next_month
