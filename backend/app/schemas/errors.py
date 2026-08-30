"""Shared Pydantic error schemas."""
from typing import List, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    error: str
    details: Optional[List[ErrorDetail]] = None
