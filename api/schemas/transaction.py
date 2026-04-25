from datetime import datetime

from pydantic import BaseModel, Field

from api.models.transaction import PaymentMethod, RecurringInterval, TransactionStatus, TransactionType


class TransactionBase(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    type: TransactionType
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    date: datetime
    isRecurring: bool = False
    recurringInterval: RecurringInterval | None = None
    receiptUrl: str | None = None
    paymentMethod: PaymentMethod = PaymentMethod.CASH


class TransactionCreateInput(TransactionBase):
    pass


class TransactionUpdateInput(BaseModel):
    title: str | None = None
    description: str | None = None
    type: TransactionType | None = None
    amount: float | None = Field(default=None, gt=0)
    category: str | None = None
    date: datetime | None = None
    isRecurring: bool | None = None
    recurringInterval: RecurringInterval | None = None
    receiptUrl: str | None = None
    paymentMethod: PaymentMethod | None = None


class TransactionBulkInput(BaseModel):
    transactions: list[TransactionCreateInput] = Field(min_length=1, max_length=300)


class TransactionBulkDeleteInput(BaseModel):
    transactionIds: list[str] = Field(min_length=1)


class TransactionResponse(BaseModel):
    id: str
    userId: str
    title: str
    description: str | None = None
    type: TransactionType
    amount: float
    category: str
    receiptUrl: str | None = None
    recurringInterval: RecurringInterval | None = None
    nextRecurringDate: datetime | None = None
    lastProcessed: datetime | None = None
    isRecurring: bool
    date: datetime
    status: TransactionStatus
    paymentMethod: PaymentMethod
    createdAt: datetime
    updatedAt: datetime


class TransactionListResponse(BaseModel):
    message: str
    transactions: list[TransactionResponse]
    pagination: dict


class ReceiptScanResponse(BaseModel):
    title: str = "Receipt"
    amount: float | None = None
    date: str | None = None
    description: str | None = None
    category: str | None = None
    paymentMethod: str | None = None
    type: str | None = None
    receiptUrl: str | None = None
    error: str | None = None
