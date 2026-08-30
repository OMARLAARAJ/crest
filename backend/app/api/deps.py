from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.crud import user as user_crud
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _unauthorized(detail: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise _unauthorized("Authentication required.")
    try:
        payload = decode_token(token)
    except JWTError:
        raise _unauthorized("Invalid or expired token.")

    if payload.get("type") != "access":
        raise _unauthorized("Invalid token type.")

    user_id = payload.get("sub")
    if not user_id:
        raise _unauthorized("Token missing subject.")

    user = user_crud.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise _unauthorized("User not found or inactive.")

    return user


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_token(token)
    except JWTError:
        return None
    if payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = user_crud.get_by_id(db, user_id)
    return user if user and user.is_active else None
