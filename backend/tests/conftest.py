"""Pytest fixtures for ReturnZero AI Backend test suite."""

from __future__ import annotations

import shutil
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.session as db_session_mod
from app.config import Settings
from app.db.models import OrderModel, SkuModel
from app.db.seed import seed_initial_data
from app.db.session import create_session_engine, create_session_factory, init_db, reset_db
from app.main import create_app

# Isolate all pytest runs from live backend/returnzero.db and local .env overrides
_TEST_TMP_DIR = Path(tempfile.mkdtemp(prefix="returnzero_pytest_"))
_TEST_DB_URL = f"sqlite+aiosqlite:///{(_TEST_TMP_DIR / 'test_returnzero.db').resolve().as_posix()}"

db_session_mod.engine = create_session_engine(_TEST_DB_URL)
db_session_mod.async_session_factory = create_session_factory(db_session_mod.engine)
db_session_mod.settings = Settings(DATABASE_URL=_TEST_DB_URL)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Clean up temporary pytest SQLite directory after the test session."""
    db_session_mod.engine.sync_engine.dispose()
    shutil.rmtree(_TEST_TMP_DIR, ignore_errors=True)


@pytest.fixture
def test_settings() -> Settings:
    """Provide isolated test configuration immune to local .env overrides."""
    return Settings(
        ENVIRONMENT="test",
        CORS_ORIGINS="http://localhost:3000,http://testserver,https://returnzero.demo",
        CORS_ORIGIN_REGEX=r"^https://returnzero.*\.vercel\.app$",
        DATABASE_URL=_TEST_DB_URL,
        DEMO_MODE=True,
        DEMO_TOKEN=SecretStr("returnzero-demo-secret-2026"),
        GEMINI_MODEL_ID="gemini-3.8-flash",
        PRIMARY_GEMINI_API_KEY=None,
        BACKUP_GEMINI_API_KEY=None,
        EXTRACT_RATE_LIMIT_PER_MIN=30,
        UPI_GATEWAY_FEE_PCT=0.0,
    )


@pytest.fixture(autouse=True)
async def setup_test_db() -> AsyncIterator[None]:
    """Ensure clean 150-order and 4-SKU seeded database state before each test."""
    await init_db()
    async with db_session_mod.async_session_factory() as session:
        order_count = (
            await session.execute(select(func.count()).select_from(OrderModel))
        ).scalar_one()
        sku_count = (await session.execute(select(func.count()).select_from(SkuModel))).scalar_one()
        sku_01 = (
            await session.execute(select(SkuModel).where(SkuModel.id == "SKU-01"))
        ).scalar_one_or_none()
        sku_03 = (
            await session.execute(select(SkuModel).where(SkuModel.id == "SKU-03"))
        ).scalar_one_or_none()
        skus_intact = (
            sku_count == 4
            and sku_01 is not None
            and sku_01.provenance == "manual_fixture"
            and len(sku_01.sizes_json) == 4
            and sku_01.sizes_json.get("M", {}).get("shoulder") == 15.5
            and sku_03 is not None
            and sku_03.has_sleeve is False
        )
        if order_count != 150 or not skus_intact:
            await reset_db()
            async with db_session_mod.async_session_factory() as s2:
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
    """Provide async database session bound to the isolated session factory."""
    async with db_session_mod.async_session_factory() as session:
        yield session
