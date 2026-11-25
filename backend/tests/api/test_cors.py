"""Tests for CORS policy configuration per ADR-008."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_allowed_origin(async_client: AsyncClient) -> None:
    """Verify requests with allowed origin receive appropriate CORS headers."""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
    }
    response = await async_client.options("/healthz", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    # ADR-008: credentials must not be allowed
    assert response.headers.get("access-control-allow-credentials") != "true"


@pytest.mark.asyncio
async def test_cors_disallowed_origin(async_client: AsyncClient) -> None:
    """Verify disallowed origins do not receive allow-origin header."""
    headers = {
        "Origin": "https://unauthorized-domain.com",
        "Access-Control-Request-Method": "GET",
    }
    response = await async_client.options("/healthz", headers=headers)
    assert response.headers.get("access-control-allow-origin") is None


@pytest.mark.asyncio
async def test_cors_vercel_preview_regex_allowed(async_client: AsyncClient) -> None:
    """Verify ReturnZero Vercel preview subdomains match allow_origin_regex without wildcard."""
    preview_origin = "https://returnzero-ai-git-feature-demo.vercel.app"
    response = await async_client.options(
        "/healthz",
        headers={"Origin": preview_origin, "Access-Control-Request-Method": "GET"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == preview_origin
    assert response.headers.get("access-control-allow-credentials") != "true"

    spoofed_origin = "https://evil-returnzero.vercel.app"
    spoof_resp = await async_client.options(
        "/healthz",
        headers={"Origin": spoofed_origin, "Access-Control-Request-Method": "GET"},
    )
    assert spoof_resp.headers.get("access-control-allow-origin") is None
