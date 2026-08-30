"""In-memory catalog of programs and subscription packs.

Kept in code (rather than DB) because this content is marketing copy that is
edited by the team via deployment, not by end-users. Returning through the
API keeps the frontend decoupled and lets us add an admin panel later
without touching the SPA.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from app.schemas.catalog import PackPublic, ProgramPublic


_NOW = datetime(2024, 1, 1, tzinfo=timezone.utc)

_PROGRAMS: Dict[str, ProgramPublic] = {
    p.id: p
    for p in [
        ProgramPublic(
            id=str(uuid.uuid4()),
            slug="built-different",
            title="Built Different",
            description=(
                "A progressive strength system engineered for a body that "
                "performs — periodized, trackable, and ruthlessly effective."
            ),
            category="strength",
            image_url=(
                "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e"
                "?auto=format&fit=crop&w=1200&q=85"
            ),
            language="en",
            created_at=_NOW,
        ),
        ProgramPublic(
            id=str(uuid.uuid4()),
            slug="peak-condition",
            title="Peak Condition",
            description=(
                "Build an engine that keeps going when others stop. "
                "Conditioning circuits, intervals, and aerobic base work."
            ),
            category="conditioning",
            image_url=(
                "https://images.unsplash.com/photo-1517836357463-d25dfeac3438"
                "?auto=format&fit=crop&w=1200&q=85"
            ),
            language="en",
            created_at=_NOW,
        ),
        ProgramPublic(
            id=str(uuid.uuid4()),
            slug="move-free",
            title="Move Free",
            description=(
                "Build resilient movement patterns and make every rep feel "
                "better. Mobility, stability, and recovery protocols."
            ),
            category="mobility",
            image_url=(
                "https://images.unsplash.com/photo-1549576490-b0b4831ef60a"
                "?auto=format&fit=crop&w=1200&q=85"
            ),
            language="en",
            created_at=_NOW,
        ),
        ProgramPublic(
            id=str(uuid.uuid4()),
            slug="fuel-forward",
            title="Fuel Forward",
            description=(
                "Nutrition built around your training, not against it. "
                "Macros, timing, and recovery meals — simplified."
            ),
            category="nutrition",
            image_url=(
                "https://images.unsplash.com/photo-1490645935967-10de6ba17061"
                "?auto=format&fit=crop&w=1200&q=85"
            ),
            language="en",
            created_at=_NOW,
        ),
    ]
}

_PACKS: Dict[str, PackPublic] = {
    p.id: p
    for p in [
        PackPublic(
            id=str(uuid.uuid4()),
            slug="base",
            name="Base",
            description="A clear start for a consistent practice.",
            price=19.0,
            currency="USD",
            features=[
                "Access to 20+ programs",
                "Progress tracking dashboard",
                "Weekly training drops",
                "Mobile app access",
            ],
            is_featured=False,
            sort_order=1,
            language="en",
        ),
        PackPublic(
            id=str(uuid.uuid4()),
            slug="pro",
            name="Pro",
            description="The complete system for serious progress.",
            price=39.0,
            currency="USD",
            features=[
                "Everything in Base",
                "Adaptive training plans",
                "Coach feedback & community",
                "Priority support",
            ],
            is_featured=True,
            sort_order=2,
            language="en",
        ),
        PackPublic(
            id=str(uuid.uuid4()),
            slug="plus",
            name="Plus",
            description="Personalized attention for your biggest goals.",
            price=79.0,
            currency="USD",
            features=[
                "Everything in Pro",
                "1:1 monthly check-in",
                "Nutrition & recovery guidance",
                "Early access to new drops",
            ],
            is_featured=False,
            sort_order=3,
            language="en",
        ),
    ]
}


def list_programs() -> List[ProgramPublic]:
    return list(_PROGRAMS.values())


def get_program(program_id: str) -> ProgramPublic | None:
    return _PROGRAMS.get(program_id)


def get_program_by_slug(slug: str) -> ProgramPublic | None:
    for program in _PROGRAMS.values():
        if program.slug == slug:
            return program
    return None


def list_packs() -> List[PackPublic]:
    return sorted(_PACKS.values(), key=lambda pack: pack.sort_order)


def get_pack(pack_id: str) -> PackPublic | None:
    return _PACKS.get(pack_id)


def get_pack_by_slug(slug: str) -> PackPublic | None:
    for pack in _PACKS.values():
        if pack.slug == slug:
            return pack
    return None
