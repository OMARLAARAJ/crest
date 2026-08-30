from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ---------- Programs ----------
class ProgramBase(BaseModel):
    slug: str = Field(min_length=2, max_length=64, pattern=r"^[a-z0-9][a-z0-9\-]*$")
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=2, max_length=500)
    category: Literal["strength", "conditioning", "mobility", "nutrition"]
    image_url: str = Field(max_length=500)
    language: Literal["en", "ar"] = "en"


class ProgramPublic(ProgramBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


# ---------- Packs ----------
class PackBase(BaseModel):
    slug: str = Field(min_length=2, max_length=64, pattern=r"^[a-z0-9][a-z0-9\-]*$")
    name: str = Field(min_length=2, max_length=60)
    description: str = Field(min_length=2, max_length=240)
    price: float = Field(ge=0, le=10000)
    currency: Literal["USD"] = "USD"
    features: List[str] = Field(min_length=1, max_length=20)
    is_featured: bool = False
    language: Literal["en", "ar"] = "en"


class PackPublic(PackBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sort_order: int


# ---------- Checkout ----------
class CheckoutRequest(BaseModel):
    item_type: Literal["program", "pack"]
    item_id: str
    success_url: Optional[str] = Field(default=None, max_length=500)
    cancel_url: Optional[str] = Field(default=None, max_length=500)


class CheckoutSession(BaseModel):
    checkout_id: str
    item_type: Literal["program", "pack"]
    item_id: str
    item_title: str
    amount: float
    currency: str
    status: Literal["pending", "completed", "cancelled"] = "pending"
    redirect_url: str
    created_at: datetime


# ---------- Contact ----------
class ContactMessageCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    subject: str = Field(min_length=2, max_length=140)
    message: str = Field(min_length=10, max_length=2000)
    language: Literal["en", "ar"] = "en"

    @field_validator("name", "subject", "message")
    @classmethod
    def _strip(cls, value: str) -> str:
        return value.strip()


class ContactMessagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: EmailStr
    subject: str
    received_at: datetime


# ---------- Generic ----------
class HealthResponse(BaseModel):
    status: Literal["ok"]
    app: str
    version: str
    environment: str
