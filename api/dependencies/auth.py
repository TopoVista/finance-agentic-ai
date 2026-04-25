from fastapi import Cookie, Depends, Header, HTTPException, status

from api.core.config import settings
from api.core.security import InvalidTokenError, parse_token
from api.models.user import User


async def get_current_user(
    authorization: str | None = Header(default=None),
    access_token_cookie: str | None = Cookie(default=None, alias=settings.COOKIE_NAME),
) -> User:
    token = authorization or access_token_cookie
    try:
        payload = parse_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


CurrentUser = Depends(get_current_user)
