from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app import catalog
from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.catalog import CheckoutRequest, CheckoutSession

router = APIRouter(prefix="/checkout", tags=["checkout"])


def _build_session(
    item_type: str,
    item_id: str,
    title: str,
    amount: float,
    success_url: str | None,
    cancel_url: str | None,
) -> CheckoutSession:
    checkout_id = str(uuid.uuid4())
    base = success_url or f"{settings.APP_BASE_URL}/checkout/success"
    redirect = f"{base}?checkout_id={checkout_id}"
    return CheckoutSession(
        checkout_id=checkout_id,
        item_type=item_type,  # type: ignore[arg-type]
        item_id=item_id,
        item_title=title,
        amount=amount,
        currency="USD",
        status="pending",
        redirect_url=redirect,
        created_at=datetime.now(timezone.utc),
    )


@router.post(
    "",
    response_model=CheckoutSession,
    status_code=status.HTTP_201_CREATED,
    summary="Create a checkout session for a program or pack",
)
def create_checkout(
    payload: CheckoutRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
) -> CheckoutSession:
    if payload.item_type == "program":
        program = catalog.get_program(payload.item_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Program not found."
            )
        # Programs are free for members; create a $0 enrollment session.
        return _build_session(
            item_type="program",
            item_id=program.id,
            title=program.title,
            amount=0.0,
            success_url=payload.success_url,
            cancel_url=payload.cancel_url,
        )

    pack = catalog.get_pack(payload.item_id)
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pack not found."
        )
    return _build_session(
        item_type="pack",
        item_id=pack.id,
        title=pack.name,
        amount=pack.price,
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
    )
