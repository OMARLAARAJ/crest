from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api import auth as auth_router
from app.api import catalog as catalog_router
from app.api import checkout as checkout_router
from app.api import contact as contact_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.limiter import limiter
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.schemas.catalog import HealthResponse
from app.schemas.errors import ErrorResponse


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=__version__,
        description=(
            "REST API powering the CREST sports platform landing page. "
            "All endpoints are versioned under /api/v1."
        ),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Rate limiter — applied per route via decorators and as a global fallback.
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Trusted hosts (defense-in-depth against host header injection).
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.APP_ENV == "development" else [
            "localhost",
            "127.0.0.1",
            "crest.local",
        ],
    )

    # CORS — only the configured origins may call the API.
    origins = settings.frontend_origins or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
        max_age=600,
    )

    # Security headers (CSP, HSTS, etc.).
    primary_origin = (settings.frontend_origins or [""])[0]
    app.add_middleware(SecurityHeadersMiddleware, csp_origin=primary_origin)

    # ---------- Routes ----------
    @app.get("/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            app=settings.APP_NAME,
            version=__version__,
            environment=settings.APP_ENV,
        )

    api_prefix = "/api/v1"
    app.include_router(auth_router.router, prefix=api_prefix)
    app.include_router(catalog_router.router, prefix=api_prefix)
    app.include_router(checkout_router.router, prefix=api_prefix)
    app.include_router(contact_router.router, prefix=api_prefix)

    # ---------- Error handlers ----------
    @app.exception_handler(StarletteHTTPException)
    async def _http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(error=str(exc.detail)).model_dump(),
            headers=exc.headers or {},
        )

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Avoid leaking stack traces; log server-side instead.
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error="Internal server error.").model_dump(),
        )

    @app.on_event("startup")
    def _on_startup() -> None:
        # Auto-create tables for development convenience. In production, run
        # `alembic upgrade head` as a separate step. Failures here are logged
        # but do not block the API from serving — Alembic is the source of
        # truth for schema migrations.
        if settings.APP_ENV == "development":
            try:
                Base.metadata.create_all(bind=engine)
            except Exception as exc:  # pragma: no cover
                import logging

                logging.getLogger("crest.startup").warning(
                    "create_all skipped: %s", exc
                )

    return app


app = create_app()
