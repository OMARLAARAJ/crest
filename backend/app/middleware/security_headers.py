"""HTTP security headers middleware."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach a strict set of security headers to every response."""

    def __init__(self, app, csp_origin: str | None = None) -> None:
        super().__init__(app)
        self.csp_origin = csp_origin or ""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=()",
        )
        # HSTS only makes sense behind HTTPS; only enable when configured.
        if request.url.scheme == "https":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=63072000; includeSubDomains",
            )
        # CSP: allow our own frontend origin + inline styles for the SPA.
        connect_src = " 'self'" + (f" {self.csp_origin}" if self.csp_origin else "")
        img_src = " 'self' data: https:"
        csp = (
            "default-src 'self'; "
            f"connect-src{connect_src}; "
            f"img-src{img_src}; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "script-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self';"
        )
        response.headers.setdefault("Content-Security-Policy", csp)
        return response
