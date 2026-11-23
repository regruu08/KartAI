"""API router package for ReturnZero AI."""

from app.api.analytics import router as analytics_router
from app.api.catalog import router as catalog_router
from app.api.demo import router as demo_router

__all__ = ["analytics_router", "catalog_router", "demo_router"]
