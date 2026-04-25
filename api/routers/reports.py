from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.dependencies.auth import CurrentUser
from api.models.report import Report, ReportStatus
from api.models.report_setting import ReportSetting
from api.models.transaction import Transaction, TransactionType
from api.models.user import User
from api.schemas.report import UpdateReportSettingInput
from api.services.ai.report_agent import report_agent
from api.utils.helpers import calculate_next_report_date
from api.utils.serializers import serialize_report, serialize_report_setting

router = APIRouter()


@router.get("/all")
async def get_all_reports(current_user: User = CurrentUser, pageSize: int = 20, pageNumber: int = 1):
    skip = (pageNumber - 1) * pageSize
    reports = await Report.find(Report.user_id == str(current_user.id)).sort("-created_at").skip(skip).limit(pageSize).to_list()
    total_count = await Report.find(Report.user_id == str(current_user.id)).count()
    report_setting = await ReportSetting.find_one(ReportSetting.user_id == str(current_user.id))
    return {
        "message": "Reports history fetched successfully",
        "reports": [serialize_report(report) for report in reports],
        "pagination": {
            "pageSize": pageSize,
            "pageNumber": pageNumber,
            "totalCount": total_count,
            "totalPages": (total_count + pageSize - 1) // pageSize,
            "skip": skip,
        },
        "reportSetting": serialize_report_setting(report_setting),
    }


@router.put("/update-setting")
async def update_report_setting(data: UpdateReportSettingInput, current_user: User = CurrentUser):
    report_setting = await ReportSetting.find_one(ReportSetting.user_id == str(current_user.id))
    if not report_setting:
        raise HTTPException(status_code=404, detail="Report setting not found")

    if data.isEnabled is not None:
        report_setting.is_enabled = data.isEnabled
        report_setting.next_report_date = calculate_next_report_date(report_setting.last_sent_date) if data.isEnabled else None

    await report_setting.save()
    return {"message": "Reports setting updated successfully"}


@router.get("/generate")
async def generate_report(current_user: User = CurrentUser, from_date: datetime | None = None, to_date: datetime | None = None):
    if not from_date or not to_date:
        raise HTTPException(status_code=400, detail="from and to query parameters are required")

    transactions = await Transaction.find(
        Transaction.user_id == str(current_user.id),
        Transaction.date >= from_date,
        Transaction.date <= to_date,
    ).to_list()

    income = sum(tx.amount for tx in transactions if tx.type == TransactionType.INCOME)
    expenses = sum(tx.amount for tx in transactions if tx.type == TransactionType.EXPENSE)
    if income == 0 and expenses == 0:
        return {"message": "Report generated successfully", "period": None, "summary": None, "insights": []}

    by_category: dict[str, float] = {}
    for tx in transactions:
        if tx.type == TransactionType.EXPENSE:
            by_category[tx.category] = by_category.get(tx.category, 0) + tx.amount

    period = f"{from_date.strftime('%B %d')} - {to_date.strftime('%d, %Y')}"
    summary = {
        "income": income,
        "expenses": expenses,
        "balance": income - expenses,
        "savingsRate": 0 if income <= 0 else round(((income - expenses) / income) * 100, 1),
        "topCategories": [
            {
                "name": name,
                "amount": amount,
                "percent": 0 if expenses == 0 else round((amount / expenses) * 100),
            }
            for name, amount in sorted(by_category.items(), key=lambda item: item[1], reverse=True)[:5]
        ],
    }

    agent_result = await report_agent.ainvoke(
        {
            "email": current_user.email,
            "period": period,
            "summary": summary,
        }
    )
    insights = agent_result.get("insights", [])

    report = Report(user_id=str(current_user.id), period=period, sent_date=datetime.utcnow(), status=ReportStatus.SENT)
    await report.insert()

    report_setting = await ReportSetting.find_one(ReportSetting.user_id == str(current_user.id))
    if report_setting:
        report_setting.last_sent_date = datetime.utcnow()
        report_setting.next_report_date = calculate_next_report_date(report_setting.last_sent_date)
        await report_setting.save()

    return {"message": "Report generated successfully", "period": period, "summary": summary, "insights": insights}
