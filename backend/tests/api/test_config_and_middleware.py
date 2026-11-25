"""Tests for deterministic config resolution, custom_settings DB binding, middleware, and rate limiting."""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.config import BACKEND_DIR, Settings, resolve_database_url
from app.main import create_app


def test_resolve_database_url_variants(tmp_path: Path) -> None:
    """Verify deterministic SQLite path normalization across relative, memory, absolute, and Postgres URLs."""
    # Relative SQLite resolves under BACKEND_DIR
    resolved_rel = resolve_database_url("sqlite+aiosqlite:///./returnzero.db")
    expected_posix = (BACKEND_DIR / "returnzero.db").resolve().as_posix()
    assert resolved_rel == f"sqlite+aiosqlite:///{expected_posix}"

    # :memory:, absolute paths, PostgreSQL, and unparseable strings remain untouched
    assert resolve_database_url("sqlite+aiosqlite:///:memory:") == "sqlite+aiosqlite:///:memory:"
    assert (
        resolve_database_url("sqlite+aiosqlite:////tmp/custom.db")
        == "sqlite+aiosqlite:////tmp/custom.db"
    )
    abs_win = (tmp_path / "abs.db").resolve().as_posix()
    assert resolve_database_url(f"sqlite+aiosqlite:///{abs_win}") == (
        f"sqlite+aiosqlite:///{abs_win}"
    )
    pg = "postgresql+asyncpg://user:pass@localhost:5432/returnzero"
    assert resolve_database_url(pg) == pg
    assert resolve_database_url("not a valid url://[") == "not a valid url://["

    # Query params preserved on relative SQLite URLs
    resolved_q = resolve_database_url("sqlite+aiosqlite:///./returnzero.db?cache=shared")
    assert resolved_q == f"sqlite+aiosqlite:///{expected_posix}?cache=shared"


def test_settings_rejects_invalid_bounds() -> None:
    """Verify Settings fails fast on negative gateway fee or non-positive timeout."""
    with pytest.raises(ValidationError):
        Settings(UPI_GATEWAY_FEE_PCT=-0.5)
    with pytest.raises(ValidationError):
        Settings(GEMINI_TIMEOUT_S=0.0)


def test_settings_loads_env_from_custom_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify Settings loads values cleanly from explicit .env file without crashing when absent."""
    monkeypatch.delenv("SERVICE_NAME", raising=False)
    monkeypatch.delenv("UPI_GATEWAY_FEE_PCT", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "SERVICE_NAME=custom-rz-api\nUPI_GATEWAY_FEE_PCT=1.25\n",
        encoding="utf-8",
    )
    s = Settings(_env_file=str(env_file))
    assert s.SERVICE_NAME == "custom-rz-api"
    assert s.UPI_GATEWAY_FEE_PCT == 1.25

    s_missing = Settings(_env_file=str(tmp_path / "does_not_exist.env"))
    assert s_missing.SERVICE_NAME == "returnzero-api"


@pytest.mark.asyncio
async def test_create_app_with_custom_memory_db_and_reset() -> None:
    """Verify create_app(custom_settings) isolates DB engine and session_factory cleanly."""
    custom = Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        DEMO_MODE=True,
        ENVIRONMENT="isolated-test",
    )
    app = create_app(custom)
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            overview = await client.get("/v1/analytics/overview")
            assert overview.status_code == 200
            assert overview.json()["total_orders"] == 150

            reset_res = await client.post(
                "/v1/demo/reset",
                headers={"X-Demo-Token": custom.DEMO_TOKEN.get_secret_value()},
            )
            assert reset_res.status_code == 200
            assert reset_res.json()["seeded_orders"] == 150


@pytest.mark.asyncio
async def test_request_id_and_structured_error_envelopes(async_client: AsyncClient) -> None:
    """Verify X-Request-ID propagation and structured error payloads across 404/422/500."""
    # 1. Echo incoming X-Request-ID on 200
    ok_res = await async_client.get("/healthz", headers={"X-Request-ID": "req-abc-123"})
    assert ok_res.status_code == 200
    assert ok_res.headers.get("x-request-id") == "req-abc-123"

    # 2. HTTPException (404) structured envelope preserving detail
    not_found = await async_client.get("/v1/catalog/skus/SKU-NOPE")
    assert not_found.status_code == 404
    body_404 = not_found.json()
    assert body_404["error"] == "NOT_FOUND"
    assert "not found" in body_404["message"].lower()
    assert body_404["detail"] == body_404["message"]
    assert body_404["request_id"] == not_found.headers.get("x-request-id")

    # 3. RequestValidationError (422) structured envelope preserving detail
    bad_pin = await async_client.post(
        "/v1/risk/evaluate",
        json={"street_address": "Flat 101, Residency", "pin_code": "123", "payment_method": "COD"},
    )
    assert bad_pin.status_code == 422
    body_422 = bad_pin.json()
    assert body_422["error"] == "VALIDATION_ERROR"
    assert isinstance(body_422["detail"], list)
    assert body_422["request_id"] == bad_pin.headers.get("x-request-id")


@pytest.mark.asyncio
async def test_unhandled_exception_returns_safe_500_envelope() -> None:
    """Verify unhandled exceptions return structured 500 JSON without leaking stack traces."""
    app = create_app(Settings(DATABASE_URL="sqlite+aiosqlite:///:memory:"))

    @app.get("/_test_boom")
    async def boom() -> None:
        raise RuntimeError("sensitive internal secret trace")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/_test_boom", headers={"X-Request-ID": "boom-req-1"})
        assert res.status_code == 500
        body = res.json()
        assert body["error"] == "INTERNAL_SERVER_ERROR"
        assert body["request_id"] == "boom-req-1"
        assert "sensitive internal secret trace" not in res.text


@pytest.mark.asyncio
async def test_extract_endpoint_per_ip_rate_limiter() -> None:
    """Verify /extract enforces EXTRACT_RATE_LIMIT_PER_MIN per client IP with HTTP 429."""
    limited_settings = Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        EXTRACT_RATE_LIMIT_PER_MIN=2,
    )
    app = create_app(limited_settings)
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers = {"X-Forwarded-For": "203.0.113.42"}
            r1 = await client.post("/v1/catalog/skus/SKU-01/extract", headers=headers)
            r2 = await client.post("/v1/catalog/skus/SKU-01/extract", headers=headers)
            r3 = await client.post("/v1/catalog/skus/SKU-01/extract", headers=headers)

            assert r1.status_code == 200
            assert r2.status_code == 200
            assert r3.status_code == 429
            assert r3.headers.get("retry-after") is not None
            assert r3.json()["error"] == "RATE_LIMIT_EXCEEDED"
