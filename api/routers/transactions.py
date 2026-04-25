from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from api.dependencies.auth import CurrentUser
from api.models.transaction import Transaction
from api.models.user import User
from api.rag.ingest import ingest_user_transactions
from api.schemas.transaction import TransactionBulkDeleteInput, TransactionBulkInput, TransactionCreateInput, TransactionUpdateInput
from api.services.ai.receipt_chain import scan_receipt_bytes
from api.services.cloudinary_service import upload_file
from api.utils.helpers import calculate_next_occurrence
from api.utils.serializers import serialize_transaction

router = APIRouter()


def _resolve_next_recurring_date(payload, existing_date: datetime | None = None):
    if payload.isRecurring and payload.recurringInterval:
        base_date = payload.date if hasattr(payload, "date") and payload.date else existing_date or datetime.now(timezone.utc)
        return calculate_next_occurrence(base_date, payload.recurringInterval)
    return None


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_transaction(data: TransactionCreateInput, current_user: User = CurrentUser):
    transaction = Transaction(
        user_id=str(current_user.id),
        title=data.title,
        description=data.description,
        type=data.type,
        amount=data.amount,
        category=data.category,
        receipt_url=data.receiptUrl,
        recurring_interval=data.recurringInterval,
        next_recurring_date=_resolve_next_recurring_date(data),
        last_processed=None,
        is_recurring=data.isRecurring,
        date=data.date,
        payment_method=data.paymentMethod,
    )
    await transaction.insert()
    await ingest_user_transactions(str(current_user.id))
    return {"message": "Transaction created successfully", "transaction": serialize_transaction(transaction)}


@router.get("/all")
async def get_all_transactions(
    current_user: User = CurrentUser,
    keyword: str | None = None,
    type: str | None = None,
    recurringStatus: str | None = None,
    pageSize: int = Query(20, ge=1, le=100),
    pageNumber: int = Query(1, ge=1),
):
    query: dict = {"user_id": str(current_user.id)}
    if keyword:
        query["$or"] = [{"title": {"$regex": keyword, "$options": "i"}}, {"category": {"$regex": keyword, "$options": "i"}}]
    if type:
        query["type"] = type
    if recurringStatus == "RECURRING":
        query["is_recurring"] = True
    elif recurringStatus == "NON_RECURRING":
        query["is_recurring"] = False

    skip = (pageNumber - 1) * pageSize
    transactions = await Transaction.find(query).sort("-created_at").skip(skip).limit(pageSize).to_list()
    total_count = await Transaction.find(query).count()

    return {
        "message": "Transaction fetched successfully",
        "transactions": [serialize_transaction(tx) for tx in transactions],
        "pagination": {
            "pageSize": pageSize,
            "pageNumber": pageNumber,
            "totalCount": total_count,
            "totalPages": (total_count + pageSize - 1) // pageSize,
            "skip": skip,
        },
    }


@router.get("/{transaction_id}")
async def get_transaction_by_id(transaction_id: str, current_user: User = CurrentUser):
    transaction = await Transaction.get(transaction_id)
    if not transaction or transaction.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction fetched successfully", "transaction": serialize_transaction(transaction)}


@router.put("/duplicate/{transaction_id}")
async def duplicate_transaction(transaction_id: str, current_user: User = CurrentUser):
    transaction = await Transaction.get(transaction_id)
    if not transaction or transaction.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Transaction not found")

    duplicated = Transaction(
        user_id=str(current_user.id),
        title=f"Duplicate - {transaction.title}",
        description=f"{transaction.description or 'Duplicated transaction'} (Duplicate)",
        type=transaction.type,
        amount=transaction.amount,
        category=transaction.category,
        receipt_url=transaction.receipt_url,
        recurring_interval=None,
        next_recurring_date=None,
        last_processed=None,
        is_recurring=False,
        date=transaction.date,
        payment_method=transaction.payment_method,
    )
    await duplicated.insert()
    await ingest_user_transactions(str(current_user.id))
    return {"message": "Transaction duplicated successfully", "data": serialize_transaction(duplicated)}


@router.put("/update/{transaction_id}")
async def update_transaction(transaction_id: str, data: TransactionUpdateInput, current_user: User = CurrentUser):
    transaction = await Transaction.get(transaction_id)
    if not transaction or transaction.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_map = data.model_dump(exclude_unset=True)
    if "receiptUrl" in update_map:
        update_map["receipt_url"] = update_map.pop("receiptUrl")
    if "recurringInterval" in update_map:
        update_map["recurring_interval"] = update_map.pop("recurringInterval")
    if "isRecurring" in update_map:
        update_map["is_recurring"] = update_map.pop("isRecurring")
    if "paymentMethod" in update_map:
        update_map["payment_method"] = update_map.pop("paymentMethod")

    for key, value in update_map.items():
        setattr(transaction, key, value)

    if transaction.is_recurring and transaction.recurring_interval:
        transaction.next_recurring_date = calculate_next_occurrence(transaction.date, transaction.recurring_interval)
    else:
        transaction.next_recurring_date = None

    await transaction.save()
    await ingest_user_transactions(str(current_user.id))
    return {"message": "Transaction updated successfully"}


@router.delete("/delete/{transaction_id}")
async def delete_transaction(transaction_id: str, current_user: User = CurrentUser):
    transaction = await Transaction.get(transaction_id)
    if not transaction or transaction.user_id != str(current_user.id):
        raise HTTPException(status_code=404, detail="Transaction not found")
    await transaction.delete()
    await ingest_user_transactions(str(current_user.id))
    return {"message": "Transaction deleted successfully"}


@router.delete("/bulk-delete")
async def bulk_delete_transactions(data: TransactionBulkDeleteInput, current_user: User = CurrentUser):
    transactions = []
    for transaction_id in data.transactionIds:
        transaction = await Transaction.get(transaction_id)
        if transaction and transaction.user_id == str(current_user.id):
            transactions.append(transaction)
    deleted_count = 0
    for transaction in transactions:
        await transaction.delete()
        deleted_count += 1
    await ingest_user_transactions(str(current_user.id))
    return {"message": "Transaction deleted successfully", "success": True, "deletedCount": deleted_count}


@router.post("/bulk-transaction")
async def bulk_create_transactions(data: TransactionBulkInput, current_user: User = CurrentUser):
    records = []
    for payload in data.transactions:
        records.append(
            Transaction(
                user_id=str(current_user.id),
                title=payload.title,
                description=payload.description,
                type=payload.type,
                amount=payload.amount,
                category=payload.category,
                receipt_url=payload.receiptUrl,
                recurring_interval=None,
                next_recurring_date=None,
                last_processed=None,
                is_recurring=False,
                date=payload.date,
                payment_method=payload.paymentMethod,
            )
        )
    if records:
        await Transaction.insert_many(records)
        await ingest_user_transactions(str(current_user.id))
    return {"message": "Bulk transaction inserted successfully", "insertedCount": len(records), "success": True}


@router.post("/scan-receipt", response_model=dict)
async def scan_receipt(receipt: UploadFile = File(...)):
    file_bytes = await receipt.read()
    uploaded_url = await upload_file(file_bytes, "finora/receipts")
    result = await scan_receipt_bytes(file_bytes, receipt.content_type or "image/jpeg", receipt_url=uploaded_url)
    return {"message": "Receipt scanned successfully", "data": result}
