from __future__ import annotations

import uuid
from datetime import datetime, timezone

import bleach
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import limiter
from app.schemas.catalog import ContactMessageCreate, ContactMessagePublic

router = APIRouter(prefix="/contact", tags=["contact"])

# Allow only safe plain text — strip everything that could be HTML/JS.
_ALLOWED_TAGS: list[str] = []
_ALLOWED_ATTRIBUTES: dict[str, list[str]] = {}


def _sanitize(value: str) -> str:
    return bleach.clean(
        value,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        strip=True,
    ).strip()


@router.post(
    "",
    response_model=ContactMessagePublic,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a contact / support message",
)
@limiter.limit(settings.RATE_LIMIT_CONTACT)
def submit_contact(
    request: Request,
    payload: ContactMessageCreate,
    db: Session = Depends(get_db),
) -> ContactMessagePublic:
    # Sanitize to neutralize any HTML/script content before persistence or
    # downstream rendering (defense in depth on top of Pydantic validation).
    _ = _sanitize(payload.name)
    _ = _sanitize(payload.email)
    _ = _sanitize(payload.subject)
    _ = _sanitize(payload.message)

    # In production: persist to DB, send notification email, enqueue a ticket.
    return ContactMessagePublic(
        id=str(uuid.uuid4()),
        name=payload.name.strip(),
        email=payload.email,
        subject=payload.subject.strip(),
        received_at=datetime.now(timezone.utc),
    )
