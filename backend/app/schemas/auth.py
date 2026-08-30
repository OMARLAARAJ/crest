from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class TokenPair(BaseModel):
    """Access + refresh token pair returned on login/register/refresh."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int  # seconds until the access token expires


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
