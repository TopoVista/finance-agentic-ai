from datetime import datetime

from pydantic import BaseModel


class SavingRate(BaseModel):
    percentage: float
    expenseRatio: float


class PreviousValues(BaseModel):
    incomeAmount: float
    expenseAmount: float
    balanceAmount: float


class PercentageChange(BaseModel):
    income: float
    expenses: float
    balance: float
    prevPeriodFrom: datetime | None = None
    prevPeriodTo: datetime | None = None
    previousValues: PreviousValues


class RangeMeta(BaseModel):
    from_date: datetime | None = None
    to_date: datetime | None = None
    value: str
    label: str


class SummaryAnalyticsResponse(BaseModel):
    availableBalance: float
    totalIncome: float
    totalExpenses: float
    savingRate: SavingRate
    transactionCount: int
    percentageChange: PercentageChange
    preset: RangeMeta


class ChartPoint(BaseModel):
    date: str
    income: float
    expenses: float


class ChartAnalyticsResponse(BaseModel):
    chartData: list[ChartPoint]
    totalIncomeCount: int
    totalExpenseCount: int
    preset: RangeMeta


class ExpenseBreakdownItem(BaseModel):
    name: str
    value: float
    percentage: float


class ExpenseBreakdownResponse(BaseModel):
    totalSpent: float
    breakdown: list[ExpenseBreakdownItem]
    preset: RangeMeta
