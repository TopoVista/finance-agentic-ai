from fastapi import APIRouter, File, Form, UploadFile

from api.dependencies.auth import CurrentUser
from api.models.user import User
from api.schemas.user import UserResponse
from api.services.cloudinary_service import upload_file
from api.utils.serializers import serialize_user

router = APIRouter()


@router.get("/current-user", response_model=dict)
async def get_current_user_profile(current_user: User = CurrentUser):
    return {"message": "User fetched successfully", "user": serialize_user(current_user)}


@router.put("/update", response_model=dict)
async def update_user_profile(
    current_user: User = CurrentUser,
    name: str = Form(...),
    profilePicture: UploadFile | None = File(default=None),
):
    current_user.name = name
    if profilePicture:
        uploaded_url = await upload_file(await profilePicture.read(), "finora/profile-pictures", public_id=str(current_user.id))
        if uploaded_url:
            current_user.profile_picture = uploaded_url
    await current_user.save()
    return {"message": "User profile updated successfully", "data": serialize_user(current_user)}
