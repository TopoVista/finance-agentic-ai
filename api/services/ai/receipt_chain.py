import base64
import json

from api.core.config import settings

RECEIPT_PROMPT = """
You extract transaction details from receipt images.
Return strict JSON with these keys:
title, amount, date, description, category, paymentMethod, type.
Use null when a field is unclear.
"""


async def scan_receipt_bytes(file_bytes: bytes, mime_type: str, receipt_url: str | None = None) -> dict:
    if not settings.GOOGLE_API_KEY:
        return {"error": "GOOGLE_API_KEY is not configured"}

    try:
        from langchain_core.messages import HumanMessage
        from langchain_google_genai import ChatGoogleGenerativeAI
    except Exception as exc:
        return {"error": f"AI dependencies unavailable: {exc}"}

    encoded = base64.b64encode(file_bytes).decode("utf-8")
    model = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0,
    )
    message = HumanMessage(
        content=[
            {"type": "text", "text": RECEIPT_PROMPT},
            {"type": "image_url", "image_url": f"data:{mime_type};base64,{encoded}"},
        ]
    )
    try:
        response = await model.ainvoke([message])
        raw = getattr(response, "content", "")
        if isinstance(raw, list):
            raw = "".join(part.get("text", "") for part in raw if isinstance(part, dict))
        cleaned = str(raw).replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)
        data["receiptUrl"] = receipt_url
        return data
    except Exception:
        return {"error": "Receipt scanning service unavailable"}
