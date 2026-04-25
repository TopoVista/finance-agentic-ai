from fastapi import APIRouter, File, UploadFile

from api.services.ai.receipt_chain import scan_receipt_bytes
from api.services.cloudinary_service import upload_file

router = APIRouter()


@router.post("/scan-receipt")
async def scan_receipt(receipt: UploadFile = File(...)):
    file_bytes = await receipt.read()
    uploaded_url = await upload_file(file_bytes, "finora/receipts")
    result = await scan_receipt_bytes(file_bytes, receipt.content_type or "image/jpeg", uploaded_url)
    return {"message": "Receipt scanned successfully", "data": result}
