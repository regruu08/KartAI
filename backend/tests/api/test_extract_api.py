"""API Integration tests for POST /v1/catalog/skus/{sku_id}/extract.

Tests endpoint execution, database persistence, provenance tags, cache hits,
force refresh, and 404 handling per ADR-006, ADR-007, ADR-013, ADR-016.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.repositories import SkuRepository
from app.db.session import async_session_factory
from app.integrations.gemini.cache import get_catalog_cache
from app.main import app


@pytest.mark.asyncio
async def test_extract_sku_success_persists_to_db() -> None:
    """Verify POST /v1/catalog/skus/{sku_id}/extract executes and updates database record."""
    # Clear cache before test
    get_catalog_cache().clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/catalog/skus/SKU-01/extract")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "SKU-01"
    assert data["provenance"] in ("manual_fixture", "live_gemini")
    assert data["extracted_at"] is not None
    assert data["prompt_version"] == "v1.0"
    assert len(data["sizes_json"]) >= 4

    # Verify database persistence
    async with async_session_factory() as session:
        repo = SkuRepository(session)
        db_sku = await repo.get_by_id("SKU-01")
        assert db_sku is not None
        assert db_sku.provenance == data["provenance"]
        assert db_sku.extracted_at is not None
        assert db_sku.prompt_version == "v1.0"


@pytest.mark.asyncio
async def test_extract_sku_second_call_hits_cache() -> None:
    """Verify second call for the same SKU returns provenance='cached'."""
    get_catalog_cache().clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First call loads into cache
        resp1 = await client.post("/v1/catalog/skus/SKU-02/extract")
        assert resp1.status_code == 200
        assert resp1.json()["provenance"] in ("manual_fixture", "live_gemini")

        # Second call hits cache
        resp2 = await client.post("/v1/catalog/skus/SKU-02/extract")
        assert resp2.status_code == 200
        assert resp2.json()["provenance"] == "cached"


@pytest.mark.asyncio
async def test_extract_sku_force_refresh_bypasses_cache() -> None:
    """Verify force_refresh=True bypasses the in-memory cache."""
    get_catalog_cache().clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First call
        resp1 = await client.post("/v1/catalog/skus/SKU-04/extract")
        assert resp1.status_code == 200

        # Second call with force_refresh
        resp2 = await client.post(
            "/v1/catalog/skus/SKU-04/extract",
            json={"force_refresh": True},
        )
        assert resp2.status_code == 200
        # When force_refresh is True, it does not return cached provenance
        assert resp2.json()["provenance"] in ("manual_fixture", "live_gemini")


@pytest.mark.asyncio
async def test_extract_sku_not_found_returns_404() -> None:
    """Verify POST /v1/catalog/skus/NON_EXISTENT/extract returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/catalog/skus/NON_EXISTENT_SKU/extract")

    assert response.status_code == 404
    assert "not found in catalog" in response.json()["detail"]


@pytest.mark.asyncio
async def test_extract_sku_03_honors_missing_sleeve_flag() -> None:
    """Verify SKU-03 extraction correctly marks has_sleeve=False in DB per ADR-004 & ADR-013."""
    get_catalog_cache().clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/catalog/skus/SKU-03/extract")

    assert response.status_code == 200
    data = response.json()
    assert data["has_sleeve"] is False

    # Check DB model
    async with async_session_factory() as session:
        repo = SkuRepository(session)
        db_sku = await repo.get_by_id("SKU-03")
        assert db_sku is not None
        assert db_sku.has_sleeve is False
