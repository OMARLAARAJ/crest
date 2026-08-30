"""Security helpers: password hashing (Argon2) and JWT handling."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    if not plain_password or len(plain_password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time verification of a plaintext password against an Argon2 hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: Optional[Mapping[str, Any]] = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "type": token_type,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    subject: str, extra_claims: Optional[Mapping[str, Any]] = None
) -> str:
    return _create_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims=extra_claims,
    )


def create_refresh_token(
    subject: str, extra_claims: Optional[Mapping[str, Any]] = None
) -> str:
    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        extra_claims=extra_claims,
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode a JWT, raising JWTError on invalid/expired tokens."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:  # surface as-is; routers translate to 401
        raise exc
