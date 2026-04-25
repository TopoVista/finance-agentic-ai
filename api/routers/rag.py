from fastapi import APIRouter, HTTPException

from api.dependencies.auth import CurrentUser
from api.models.user import User
from api.schemas.rag import RagChatInput
from api.rag.chains.finance_qa import build_finance_qa_chain
from api.rag.ingest import ingest_user_transactions
from api.core.config import settings

router = APIRouter()


@router.post("/chat")
async def finance_chat(data: RagChatInput, current_user: User = CurrentUser):
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="GOOGLE_API_KEY is not configured")

    await ingest_user_transactions(str(current_user.id))
    chain = build_finance_qa_chain(str(current_user.id))
    result = await chain.ainvoke({"input": data.question})
    context = result.get("context", [])
    return {
        "answer": result.get("answer", ""),
        "sources": [
            {
                "transactionId": doc.metadata.get("transaction_id"),
                "category": doc.metadata.get("category"),
            }
            for doc in context
        ],
    }
