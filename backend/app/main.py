"""ReturnZero AI — FastAPI Application Entrypoint.

Provides FastAPI app factory, CORS middleware configuration (ADR-008),
lifespan handler, and canonical API routes per ADR-005, ADR-006, ADR-007, and ADR-009.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.analytics import router as analytics_router
from app.api.catalog import router as catalog_router
from app.api.demo import router as demo_router
from app.config import Settings, get_settings
from app.db.seed import seed_initial_data
from app.db.session import async_session_factory, engine, init_db


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
    # Startup: Database schema initialization and idempotent 150-order seeding
    await init_db()
    async with async_session_factory() as session:
        await seed_initial_data(session)
        await session.commit()
    yield
    # Shutdown: Cleanly close pools and background connections
    await engine.dispose()


def create_app(custom_settings: Settings | None = None) -> FastAPI:
    """FastAPI application factory."""
    settings = custom_settings or get_settings()

    app = FastAPI(
        title="ReturnZero AI API",
        description="Fit Intelligence & Delivery Assurance Layer for D2C Fashion",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ADR-008: Strict CORS configuration (no wildcard with credentials)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Canonical API Routers
    app.include_router(catalog_router, prefix="/v1/catalog", tags=["Catalog"])
    app.include_router(analytics_router, prefix="/v1/analytics", tags=["Analytics"])
    app.include_router(demo_router, prefix="/v1/demo", tags=["Demo"])

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
            "service": settings.SERVICE_NAME,
            "timestamp": datetime.now(UTC).isoformat(),
            "environment": settings.ENVIRONMENT,
            "model_id": settings.GEMINI_MODEL_ID,
            "gemini_configured": settings.has_gemini_key,
        }

    return app


# Module-level default application instance
app = create_app()
