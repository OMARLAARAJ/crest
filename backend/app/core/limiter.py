"""Module-level SlowAPI Limiter.

We need a single shared Limiter instance so route decorators can reference it
at import time. It is also attached to `app.state.limiter` for compatibility
with the SlowAPI exception handler.
"""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
)
