from datetime import datetime, timezone
from enum import Enum

from beanie import Document, Indexed
from pydantic import Field


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RecurringInterval(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class PaymentMethod(str, Enum):
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    MOBILE_PAYMENT = "MOBILE_PAYMENT"
    AUTO_DEBIT = "AUTO_DEBIT"
    CASH = "CASH"
    OTHER = "OTHER"


class Transaction(Document):
    user_id: Indexed(str)  # type: ignore[valid-type]
    type: TransactionType
    title: str = Field(min_length=1)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    receipt_url: str | None = None
    recurring_interval: RecurringInterval | None = None
    next_recurring_date: datetime | None = None
    last_processed: datetime | None = None
    is_recurring: bool = False
    description: str | None = None
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: TransactionStatus = TransactionStatus.COMPLETED
    payment_method: PaymentMethod = PaymentMethod.CASH
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "transactions"
        indexes = ["user_id", [("user_id", 1), ("date", -1)]]

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
