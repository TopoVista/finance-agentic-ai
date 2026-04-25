from datetime import datetime, timedelta, timezone
from enum import Enum


class DateRangeEnum(str, Enum):
    LAST_30_DAYS = "30days"
    LAST_MONTH = "lastMonth"
    LAST_3_MONTHS = "last3Months"
    LAST_YEAR = "lastYear"
    THIS_MONTH = "thisMonth"
    THIS_YEAR = "thisYear"
    ALL_TIME = "allTime"
    CUSTOM = "custom"


def _month_start(date: datetime) -> datetime:
    return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _year_start(date: datetime) -> datetime:
    return date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def get_date_range(
    preset: DateRangeEnum | None = None,
    custom_from: datetime | None = None,
    custom_to: datetime | None = None,
) -> dict:
    if custom_from and custom_to:
        return {
            "from": custom_from,
            "to": custom_to,
            "value": DateRangeEnum.CUSTOM.value,
            "label": "Custom",
        }

    now = datetime.now(timezone.utc)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    last_30 = {
        "from": today_end - timedelta(days=29),
        "to": today_end,
        "value": DateRangeEnum.LAST_30_DAYS.value,
        "label": "Last 30 Days",
    }

    if preset == DateRangeEnum.ALL_TIME:
        return {"from": None, "to": None, "value": DateRangeEnum.ALL_TIME.value, "label": "All Time"}
    if preset == DateRangeEnum.LAST_MONTH:
        this_month = _month_start(now)
        last_month_end = this_month - timedelta(microseconds=1)
        last_month_start = _month_start(last_month_end)
        return {"from": last_month_start, "to": last_month_end, "value": preset.value, "label": "Last Month"}
    if preset == DateRangeEnum.LAST_3_MONTHS:
        this_month = _month_start(now)
        start = _month_start((this_month - timedelta(days=90)))
        end = this_month - timedelta(microseconds=1)
        return {"from": start, "to": end, "value": preset.value, "label": "Last 3 Months"}
    if preset == DateRangeEnum.LAST_YEAR:
        this_year = _year_start(now)
        last_year_end = this_year - timedelta(microseconds=1)
        last_year_start = _year_start(last_year_end)
        return {"from": last_year_start, "to": last_year_end, "value": preset.value, "label": "Last Year"}
    if preset == DateRangeEnum.THIS_MONTH:
        return {"from": _month_start(now), "to": today_end, "value": preset.value, "label": "This Month"}
    if preset == DateRangeEnum.THIS_YEAR:
        return {"from": _year_start(now), "to": today_end, "value": preset.value, "label": "This Year"}
    return last_30
