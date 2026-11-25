"""API Integration tests for POST /v1/catalog/skus/{sku_id}/extract.

Tests endpoint execution, database persistence, provenance tags, cache hits,
force refresh, and 404 handling per ADR-006, ADR-007, ADR-013, ADR-016.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import SkuRepository
from app.integrations.gemini.cache import get_catalog_cache


@pytest.mark.asyncio
async def test_extract_sku_success_persists_to_db(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verify POST /v1/catalog/skus/{sku_id}/extract executes and updates database record."""
    get_catalog_cache().clear()

    response = await async_client.post("/v1/catalog/skus/SKU-01/extract")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "SKU-01"
    assert data["provenance"] in ("manual_fixture", "live_gemini")
    assert data["extracted_at"] is not None
    assert data["prompt_version"] == "v1.0"
    assert len(data["sizes_json"]) >= 4

    # Verify database persistence
    repo = SkuRepository(db_session)
    db_sku = await repo.get_by_id("SKU-01")
    assert db_sku is not None
    assert db_sku.provenance == data["provenance"]
    assert db_sku.extracted_at is not None
    assert db_sku.prompt_version == "v1.0"


@pytest.mark.asyncio
async def test_extract_sku_second_call_hits_cache(async_client: AsyncClient) -> None:
    """Verify second call for the same SKU returns provenance='cached'."""
    get_catalog_cache().clear()

    # First call loads into cache
    resp1 = await async_client.post("/v1/catalog/skus/SKU-02/extract")
    assert resp1.status_code == 200
    assert resp1.json()["provenance"] in ("manual_fixture", "live_gemini")

    # Second call hits cache
    resp2 = await async_client.post("/v1/catalog/skus/SKU-02/extract")
    assert resp2.status_code == 200
    assert resp2.json()["provenance"] == "cached"


@pytest.mark.asyncio
async def test_extract_sku_force_refresh_bypasses_cache(async_client: AsyncClient) -> None:
    """Verify force_refresh=True bypasses the in-memory cache."""
    get_catalog_cache().clear()

    # First call
    resp1 = await async_client.post("/v1/catalog/skus/SKU-04/extract")
    assert resp1.status_code == 200

    # Second call with force_refresh
    resp2 = await async_client.post(
        "/v1/catalog/skus/SKU-04/extract",
        json={"force_refresh": True},
    )
    assert resp2.status_code == 200
    # When force_refresh is True, it does not return cached provenance
    assert resp2.json()["provenance"] in ("manual_fixture", "live_gemini")


@pytest.mark.asyncio
async def test_extract_sku_not_found_returns_404(async_client: AsyncClient) -> None:
    """Verify POST /v1/catalog/skus/NON_EXISTENT/extract returns 404."""
    response = await async_client.post("/v1/catalog/skus/NON_EXISTENT_SKU/extract")

    assert response.status_code == 404
    assert "not found in catalog" in response.json()["detail"]


@pytest.mark.asyncio
async def test_extract_sku_03_honors_missing_sleeve_flag(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verify SKU-03 extraction correctly marks has_sleeve=False in DB per ADR-004 & ADR-013."""
    get_catalog_cache().clear()

    response = await async_client.post("/v1/catalog/skus/SKU-03/extract")

    assert response.status_code == 200
    data = response.json()
    assert data["has_sleeve"] is False

    # Check DB model
    repo = SkuRepository(db_session)
    db_sku = await repo.get_by_id("SKU-03")
    assert db_sku is not None
    assert db_sku.has_sleeve is False
