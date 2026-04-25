import cloudinary
import cloudinary.uploader

from api.core.config import settings

if settings.CLOUDINARY_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


async def upload_file(file_bytes: bytes, folder: str, public_id: str | None = None) -> str | None:
    if not (settings.CLOUDINARY_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET):
        return None

    result = cloudinary.uploader.upload(
        file_bytes,
        folder=folder,
        public_id=public_id,
        overwrite=True,
        resource_type="auto",
    )
    return result.get("secure_url")
