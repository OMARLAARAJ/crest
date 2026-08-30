from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

AllowedLanguage = Literal["en", "ar"]


class UserCreate(BaseModel):
    """Registration payload."""

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)
    preferred_language: AllowedLanguage = "en"

    @field_validator("full_name")
    @classmethod
    def _strip_full_name(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        return cleaned


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserPublic(BaseModel):
    """Public-facing user profile (no password material)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: str
    preferred_language: AllowedLanguage
    is_active: bool
    is_verified: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    preferred_language: Optional[AllowedLanguage] = None

    @field_validator("full_name")
    @classmethod
    def _strip_full_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        return cleaned


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
