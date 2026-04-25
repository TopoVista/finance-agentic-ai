from datetime import datetime, timedelta

from fastapi import APIRouter

from api.core.database import get_database
from api.dependencies.auth import CurrentUser
from api.models.transaction import TransactionType
from api.models.user import User
from api.utils.date_ranges import DateRangeEnum, get_date_range
from api.utils.money import clamp_percentage

router = APIRouter()


def _match_stage(user_id: str, from_date: datetime | None, to_date: datetime | None):
    match: dict = {"user_id": user_id}
    if from_date and to_date:
        match["date"] = {"$gte": from_date, "$lte": to_date}
    return match


@router.get("/summary")
async def summary_analytics(
    current_user: User = CurrentUser,
    preset: DateRangeEnum | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
):
    db = get_database()
    range_meta = get_date_range(preset, from_date, to_date)
    match = _match_stage(str(current_user.id), range_meta["from"], range_meta["to"])

    pipeline = [
        {"$match": match},
        {
            "$group": {
                "_id": None,
                "totalIncome": {
                    "$sum": {"$cond": [{"$eq": ["$type", TransactionType.INCOME.value]}, "$amount", 0]}
                },
                "totalExpenses": {
                    "$sum": {"$cond": [{"$eq": ["$type", TransactionType.EXPENSE.value]}, "$amount", 0]}
                },
                "transactionCount": {"$sum": 1},
            }
        },
    ]
    current = await db["transactions"].aggregate(pipeline).to_list(length=1)
    row = current[0] if current else {}
    total_income = float(row.get("totalIncome", 0))
    total_expenses = float(row.get("totalExpenses", 0))
    available_balance = total_income - total_expenses
    savings_percentage = 0 if total_income <= 0 else round(((total_income - total_expenses) / total_income) * 100, 2)
    expense_ratio = 0 if total_income <= 0 else round((total_expenses / total_income) * 100, 2)

    percentage_change = {
        "income": 0,
        "expenses": 0,
        "balance": 0,
        "prevPeriodFrom": None,
        "prevPeriodTo": None,
        "previousValues": {"incomeAmount": 0, "expenseAmount": 0, "balanceAmount": 0},
    }

    if range_meta["from"] and range_meta["to"] and range_meta["value"] != DateRangeEnum.ALL_TIME.value:
        period_days = max(1, (range_meta["to"] - range_meta["from"]).days + 1)
        prev_from = range_meta["from"] - timedelta(days=period_days)
        prev_to = range_meta["to"] - timedelta(days=period_days)
        previous = await db["transactions"].aggregate(
            [
                {"$match": _match_stage(str(current_user.id), prev_from, prev_to)},
                {
                    "$group": {
                        "_id": None,
                        "totalIncome": {
                            "$sum": {"$cond": [{"$eq": ["$type", TransactionType.INCOME.value]}, "$amount", 0]}
                        },
                        "totalExpenses": {
                            "$sum": {"$cond": [{"$eq": ["$type", TransactionType.EXPENSE.value]}, "$amount", 0]}
                        },
                    }
                },
            ]
        ).to_list(length=1)
        previous_row = previous[0] if previous else {}
        prev_income = float(previous_row.get("totalIncome", 0))
        prev_expenses = float(previous_row.get("totalExpenses", 0))
        prev_balance = prev_income - prev_expenses

        def pct(previous_value: float, current_value: float) -> float:
            if previous_value == 0:
                return 100 if current_value else 0
            return clamp_percentage(((current_value - previous_value) / abs(previous_value)) * 100)

        percentage_change = {
            "income": pct(prev_income, total_income),
            "expenses": pct(prev_expenses, total_expenses),
            "balance": pct(prev_balance, available_balance),
            "prevPeriodFrom": prev_from,
            "prevPeriodTo": prev_to,
            "previousValues": {
                "incomeAmount": prev_income,
                "expenseAmount": prev_expenses,
                "balanceAmount": prev_balance,
            },
        }

    return {
        "message": "Summary fetched successfully",
        "data": {
            "availableBalance": available_balance,
            "totalIncome": total_income,
            "totalExpenses": total_expenses,
            "savingRate": {"percentage": savings_percentage, "expenseRatio": expense_ratio},
            "transactionCount": int(row.get("transactionCount", 0)),
            "percentageChange": percentage_change,
            "preset": {
                "from_date": range_meta["from"],
                "to_date": range_meta["to"],
                "value": range_meta["value"],
                "label": range_meta["label"],
            },
        },
    }


@router.get("/chart")
async def chart_analytics(
    current_user: User = CurrentUser,
    preset: DateRangeEnum | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
):
    db = get_database()
    range_meta = get_date_range(preset, from_date, to_date)
    result = await db["transactions"].aggregate(
        [
            {"$match": _match_stage(str(current_user.id), range_meta["from"], range_meta["to"])},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                    "income": {"$sum": {"$cond": [{"$eq": ["$type", TransactionType.INCOME.value]}, "$amount", 0]}},
                    "expenses": {"$sum": {"$cond": [{"$eq": ["$type", TransactionType.EXPENSE.value]}, "$amount", 0]}},
                    "incomeCount": {"$sum": {"$cond": [{"$eq": ["$type", TransactionType.INCOME.value]}, 1, 0]}},
                    "expenseCount": {"$sum": {"$cond": [{"$eq": ["$type", TransactionType.EXPENSE.value]}, 1, 0]}},
                }
            },
            {"$sort": {"_id": 1}},
        ]
    ).to_list(length=None)

    return {
        "message": "Chart fetched successfully",
        "data": {
            "chartData": [{"date": row["_id"], "income": row["income"], "expenses": row["expenses"]} for row in result],
            "totalIncomeCount": sum(row["incomeCount"] for row in result),
            "totalExpenseCount": sum(row["expenseCount"] for row in result),
            "preset": {
                "from_date": range_meta["from"],
                "to_date": range_meta["to"],
                "value": range_meta["value"],
                "label": range_meta["label"],
            },
        },
    }


@router.get("/expense-breakdown")
async def expense_breakdown(
    current_user: User = CurrentUser,
    preset: DateRangeEnum | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
):
    db = get_database()
    range_meta = get_date_range(preset, from_date, to_date)
    result = await db["transactions"].aggregate(
        [
            {
                "$match": {
                    **_match_stage(str(current_user.id), range_meta["from"], range_meta["to"]),
                    "type": TransactionType.EXPENSE.value,
                }
            },
            {"$group": {"_id": "$category", "value": {"$sum": "$amount"}}},
            {"$sort": {"value": -1}},
        ]
    ).to_list(length=None)
    total_spent = sum(item["value"] for item in result)
    top = result[:3]
    if len(result) > 3:
        top.append({"_id": "others", "value": sum(item["value"] for item in result[3:])})
    breakdown = [
        {
            "name": item["_id"],
            "value": item["value"],
            "percentage": 0 if total_spent == 0 else round((item["value"] / total_spent) * 100),
        }
        for item in top
    ]
    return {
        "message": "Expense breakdown fetched successfully",
        "data": {
            "totalSpent": total_spent,
            "breakdown": breakdown,
            "preset": {
                "from_date": range_meta["from"],
                "to_date": range_meta["to"],
                "value": range_meta["value"],
                "label": range_meta["label"],
            },
        },
    }
