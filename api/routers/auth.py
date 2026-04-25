from fastapi import APIRouter, HTTPException, Response, status

from api.core.config import settings
from api.core.security import create_access_token, hash_password, verify_password
from api.models.report_setting import ReportFrequency, ReportSetting
from api.models.user import User
from api.schemas.auth import AuthResponse, LoginInput, RegisterInput
from api.utils.helpers import calculate_next_report_date
from api.utils.serializers import serialize_report_setting, serialize_user

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterInput, response: Response):
    existing_user = await User.find_one(User.email == data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
    )
    await user.insert()

    report_setting = ReportSetting(
        user_id=str(user.id),
        frequency=ReportFrequency.MONTHLY,
        is_enabled=True,
        next_report_date=calculate_next_report_date(),
        last_sent_date=None,
    )
    await report_setting.insert()

    access_token, expires_at = create_access_token(str(user.id))
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {
        "message": "User registered successfully",
        "user": serialize_user(user),
        "accessToken": access_token,
        "expiresAt": expires_at,
        "reportSetting": serialize_report_setting(report_setting),
    }


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginInput, response: Response):
    user = await User.find_one(User.email == data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email/password")

    report_setting = await ReportSetting.find_one(ReportSetting.user_id == str(user.id))
    access_token, expires_at = create_access_token(str(user.id))
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {
        "message": "User logged in successfully",
        "user": serialize_user(user),
        "accessToken": access_token,
        "expiresAt": expires_at,
        "reportSetting": serialize_report_setting(report_setting),
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(settings.COOKIE_NAME)
    return {"message": "Logged out successfully"}
