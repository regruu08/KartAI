"""Pytest fixtures for ReturnZero AI Backend test suite."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import OrderModel
from app.db.seed import seed_initial_data
from app.db.session import async_session_factory, init_db, reset_db
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    """Provide isolated test configuration."""
    return Settings(
        ENVIRONMENT="test",
        CORS_ORIGINS="http://localhost:3000,http://testserver,https://returnzero.demo",
        DATABASE_URL="sqlite+aiosqlite:///./returnzero.db",
        DEMO_MODE=True,
        GEMINI_MODEL_ID="gemini-3.8-flash",
    )


@pytest.fixture(autouse=True)
async def setup_test_db() -> AsyncIterator[None]:
    """Ensure clean 150-order seeded database state before each test."""
    await init_db()
    async with async_session_factory() as session:
        count_stmt = select(func.count()).select_from(OrderModel)
        count = (await session.execute(count_stmt)).scalar_one()
        if count != 150:
            await reset_db()
            async with async_session_factory() as s2:
                await seed_initial_data(s2)
                await s2.commit()
    yield


@pytest.fixture
async def test_app(test_settings: Settings) -> AsyncIterator[FastAPI]:
    """Create FastAPI application with test settings and active lifespan."""
    app = create_app(test_settings)
    async with app.router.lifespan_context(app):
        yield app


@pytest.fixture
async def async_client(test_app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Provide async HTTP client bound to the test application."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Provide async database session bound to the session factory."""
    async with async_session_factory() as session:
        yield session
