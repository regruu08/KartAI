"""ReturnZero AI — FastAPI Application Entrypoint.

Provides FastAPI app factory, CORS middleware configuration (ADR-008),
lifespan handler, and canonical API routes per ADR-005, ADR-006, ADR-007, and ADR-009.
"""

from __future__ import annotations

import logging
import re
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from starlette.exceptions import HTTPException as StarletteHTTPException

import app.db.session as db_session
from app.api.analytics import router as analytics_router
from app.api.catalog import router as catalog_router
from app.api.demo import router as demo_router
from app.api.fit import router as fit_router
from app.api.incentive import router as incentive_router
from app.api.orders import router as orders_router
from app.api.rate_limit import SlidingWindowRateLimiter
from app.api.risk import router as risk_router
from app.config import Settings, get_settings
from app.db.seed import seed_initial_data
from app.db.session import create_session_engine, create_session_factory, init_db

logger = logging.getLogger("returnzero.api")

_REQUEST_ID_CTX: ContextVar[str] = ContextVar("request_id", default="-")
_SAFE_REQ_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

_HTTP_ERROR_CODES: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "UNPROCESSABLE_CONTENT",
    429: "RATE_LIMIT_EXCEEDED",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
}


def _resolve_request_id(request: Request) -> str:
    """Resolve an existing request_id from state/header or generate a fresh one."""
    state_id = getattr(request.state, "request_id", None)
    if isinstance(state_id, str) and state_id:
        return state_id
    incoming = request.headers.get("X-Request-ID", "").strip()
    if incoming and _SAFE_REQ_ID_RE.match(incoming):
        return incoming
    return uuid.uuid4().hex[:16]


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    environment: str
    model_id: str
    gemini_configured: bool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager for startup and shutdown routines."""
    app_engine: AsyncEngine = getattr(app.state, "engine", db_session.engine)
    app_factory: async_sessionmaker[AsyncSession] = getattr(
        app.state, "session_factory", db_session.async_session_factory
    )

    # Startup: Database schema initialization and idempotent 150-order seeding
    await init_db(engine_override=app_engine)
    async with app_factory() as session:
        await seed_initial_data(session)
        await session.commit()
    yield
    # Shutdown: Cleanly close pools and background connections
    await app_engine.dispose()


def create_app(custom_settings: Settings | None = None) -> FastAPI:
    """FastAPI application factory."""
    active_settings = custom_settings or get_settings()

    # Bind engine and session factory cleanly for custom settings (e.g. isolated test DBs)
    if custom_settings is not None and (
        active_settings.DATABASE_URL != db_session.settings.DATABASE_URL
        or ":memory:" in active_settings.DATABASE_URL
    ):
        app_engine = create_session_engine(active_settings.DATABASE_URL)
        app_session_factory = create_session_factory(app_engine)
    else:
        app_engine = db_session.engine
        app_session_factory = db_session.async_session_factory

    app = FastAPI(
        title="ReturnZero AI API",
        description="Fit Intelligence & Delivery Assurance Layer for D2C Fashion",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.state.settings = active_settings
    app.state.engine = app_engine
    app.state.session_factory = app_session_factory
    app.state.extract_rate_limiter = SlidingWindowRateLimiter(
        max_requests=active_settings.EXTRACT_RATE_LIMIT_PER_MIN,
        window_seconds=60.0,
    )

    if custom_settings is not None:
        app.dependency_overrides[get_settings] = lambda: active_settings

    # ADR-008: Strict CORS configuration (no wildcard with credentials)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins_list,
        allow_origin_regex=active_settings.cors_origin_regex,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_id_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Attach deterministic X-Request-ID to every request and response."""
        req_id = _resolve_request_id(request)
        request.state.request_id = req_id
        token = _REQUEST_ID_CTX.set(req_id)
        try:
            response = await call_next(request)
        finally:
            _REQUEST_ID_CTX.reset(token)
        response.headers["X-Request-ID"] = req_id
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Return structured error envelope while preserving status codes and detail."""
        req_id = _resolve_request_id(request)
        detail_msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        error_code = _HTTP_ERROR_CODES.get(exc.status_code, f"HTTP_{exc.status_code}")
        headers = dict(exc.headers) if exc.headers else {}
        headers["X-Request-ID"] = req_id
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": error_code,
                "message": detail_msg,
                "detail": exc.detail,
                "request_id": req_id,
            },
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Return structured 422 envelope preserving FastAPI validation error detail."""
        req_id = _resolve_request_id(request)
        errors = jsonable_encoder(exc.errors())
        summary_parts: list[str] = []
        for err in errors:
            loc = ".".join(str(part) for part in err.get("loc", ()))
            msg = str(err.get("msg", "Invalid value"))
            summary_parts.append(f"{loc}: {msg}" if loc else msg)
        summary_msg = "; ".join(summary_parts) if summary_parts else "Request validation failed."
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": "VALIDATION_ERROR",
                "message": summary_msg,
                "detail": errors,
                "request_id": req_id,
            },
            headers={"X-Request-ID": req_id},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Return structured 500 envelope without leaking tracebacks or secrets."""
        req_id = _resolve_request_id(request)
        logger.exception(
            "Unhandled application error request_id=%s path=%s",
            req_id,
            request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal error occurred.",
                "detail": "An unexpected internal error occurred.",
                "request_id": req_id,
            },
            headers={"X-Request-ID": req_id},
        )

    # Canonical API Routers
    app.include_router(catalog_router, prefix="/v1/catalog", tags=["Catalog"])
    app.include_router(fit_router, prefix="/v1/fit", tags=["Fit"])
    app.include_router(analytics_router, prefix="/v1/analytics", tags=["Analytics"])
    app.include_router(demo_router, prefix="/v1/demo", tags=["Demo"])
    app.include_router(risk_router, prefix="/v1/risk", tags=["Risk"])
    app.include_router(incentive_router, prefix="/v1/incentive", tags=["Incentive"])
    app.include_router(orders_router, prefix="/v1/orders", tags=["Orders"])

    @app.get(
        "/healthz",
        response_model=HealthCheckResponse,
        summary="Service Liveness Health Check",
        tags=["Health"],
    )
    async def healthcheck() -> dict[str, Any]:
        """Liveness health check endpoint returning service status and model configuration."""
        return {
            "status": "ok",
            "service": active_settings.SERVICE_NAME,
            "timestamp": datetime.now(UTC).isoformat(),
            "environment": active_settings.ENVIRONMENT,
            "model_id": active_settings.GEMINI_MODEL_ID,
            "gemini_configured": active_settings.has_gemini_key,
        }

    return app


# Module-level default application instance
app = create_app()
