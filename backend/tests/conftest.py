"""Pytest fixtures for ReturnZero AI Backend test suite."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    """Provide isolated test configuration."""
    return Settings(
        ENVIRONMENT="test",
        CORS_ORIGINS="http://localhost:3000,http://testserver,https://returnzero.demo",
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        DEMO_MODE=True,
        GEMINI_MODEL_ID="gemini-3.8-flash",
    )


@pytest.fixture
def test_app(test_settings: Settings) -> FastAPI:
    """Create FastAPI application with test settings."""
    return create_app(test_settings)


@pytest.fixture
async def async_client(test_app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Provide async HTTP client bound to the test application."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
