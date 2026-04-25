from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from api.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expires_at,
    }
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, expires_at


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


def normalize_bearer_token(token: str | None) -> str | None:
    if not token:
        return None
    if token.startswith("Bearer "):
        return token.split(" ", 1)[1]
    return token


class InvalidTokenError(Exception):
    pass


def parse_token(token: str | None) -> dict[str, Any]:
    normalized = normalize_bearer_token(token)
    if not normalized:
        raise InvalidTokenError("Missing token")
    try:
        return decode_access_token(normalized)
    except JWTError as exc:
        raise InvalidTokenError("Invalid token") from exc
