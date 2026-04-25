from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from api.schemas.user import ReportSettingResponse, UserResponse


class RegisterInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=4)


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


class AuthResponse(BaseModel):
    message: str
    user: UserResponse
    accessToken: str
    expiresAt: datetime
    reportSetting: ReportSettingResponse | None = None
