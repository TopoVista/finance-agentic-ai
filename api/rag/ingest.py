from langchain_core.documents import Document

from api.core.config import settings
from api.models.transaction import Transaction
from api.rag.retriever import get_vector_store


async def ingest_user_transactions(user_id: str) -> None:
    if not settings.GOOGLE_API_KEY:
        return

    vector_store = get_vector_store()
    existing = vector_store.get(where={"user_id": user_id})
    ids = existing.get("ids", []) if existing else []
    if ids:
        vector_store.delete(ids=ids)

    transactions = await Transaction.find(Transaction.user_id == user_id).to_list()
    docs = [
        Document(
            page_content=(
                f"{tx.type} transaction titled {tx.title}. "
                f"Category: {tx.category}. Amount: {tx.amount}. "
                f"Date: {tx.date.isoformat()}. Description: {tx.description or 'N/A'}."
            ),
            metadata={"user_id": user_id, "transaction_id": str(tx.id), "category": tx.category},
            id=str(tx.id),
        )
        for tx in transactions
    ]
    if docs:
        vector_store.add_documents(docs, ids=[doc.id for doc in docs if doc.id])
