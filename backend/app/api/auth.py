from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.auth import AccessToken, RefreshRequest, TokenPair
from app.schemas.user import (
    PasswordChange,
    UserCreate,
    UserLogin,
    UserPublic,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_token_pair(user: User) -> TokenPair:
    extra: dict[str, Any] = {"email": user.email}
    access = create_access_token(subject=user.id, extra_claims=extra)
    refresh = create_refresh_token(subject=user.id, extra_claims=extra)
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _set_auth_cookies(response: Response, tokens: TokenPair) -> None:
    """Mirror tokens in HttpOnly cookies in addition to the JSON body."""
    cookie_kwargs = {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": "lax",
        "path": "/",
    }
    response.set_cookie("crest_access_token", tokens.access_token, **cookie_kwargs)
    response.set_cookie("crest_refresh_token", tokens.refresh_token, **cookie_kwargs)


@router.post(
    "/register",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and return a token pair",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def register(
    request: Request,
    payload: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenPair:
    if user_crud.get_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    user = user_crud.create_user(db, payload)
    tokens = _build_token_pair(user)
    _set_auth_cookies(response, tokens)
    return tokens


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Authenticate with email + password",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
def login(
    request: Request,
    payload: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenPair:
    user = user_crud.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    tokens = _build_token_pair(user)
    _set_auth_cookies(response, tokens)
    return tokens


@router.post(
    "/refresh",
    response_model=AccessToken,
    summary="Exchange a refresh token for a fresh access token",
)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> AccessToken:
    try:
        decoded = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token type for refresh endpoint.",
        )

    user = user_crud.get_by_id(db, decoded.get("sub", ""))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )

    access = create_access_token(
        subject=user.id, extra_claims={"email": user.email}
    )
    return AccessToken(
        access_token=access,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear auth cookies",
)
def logout(response: Response) -> Response:
    response.delete_cookie("crest_access_token", path="/")
    response.delete_cookie("crest_refresh_token", path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get the currently authenticated user",
)
def read_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserPublic,
    summary="Update profile fields",
)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    updated = user_crud.update_profile(db, current_user, payload)
    return UserPublic.model_validate(updated)


@router.post(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change the current password",
)
def change_my_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    ok = user_crud.change_password(
        db, current_user, payload.current_password, payload.new_password
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
