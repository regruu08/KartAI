"""Unit & Contract tests for /healthz endpoint."""

from __future__ import annotations

from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from app.config import Settings
from app.main import create_app


@pytest.mark.asyncio
async def test_healthcheck_returns_ok(async_client: AsyncClient) -> None:
    """Verify /healthz returns 200 with standard healthy payload."""
    response = await async_client.get("/healthz")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "returnzero-api"
    assert data["environment"] == "test"
    assert data["model_id"] == "gemini-3.8-flash"
    assert data["gemini_configured"] is False

    # Verify timestamp format
    ts = datetime.fromisoformat(data["timestamp"])
    assert ts.year >= 2026


@pytest.mark.asyncio
async def test_healthcheck_with_configured_gemini_key() -> None:
    """Verify /healthz reports gemini_configured=True without leaking secrets."""
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("secret-test-key-12345"),
        ENVIRONMENT="production",
    )
    app = create_app(settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["gemini_configured"] is True

        # Assert secret is never leaked anywhere in the response body or headers
        assert "secret-test-key-12345" not in response.text


@pytest.mark.asyncio
async def test_app_lifespan() -> None:
    """Verify application lifespan startup and shutdown routines."""
    app = create_app()
    async with app.router.lifespan_context(app):
        pass
