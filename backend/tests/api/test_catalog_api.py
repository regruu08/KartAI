"""API contract tests for /v1/catalog endpoints.

Verifies catalog listing, single SKU retrieval, attribute schemas, and 404 responses.
Reference: ADR-006, ADR-007, AGENTS.md §7.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_catalog_skus_returns_curated_four(async_client: AsyncClient) -> None:
    """Verify GET /v1/catalog/skus returns the 4 curated fashion SKUs."""
    response = await async_client.get("/v1/catalog/skus")
    assert response.status_code == 200

    data = response.json()
    assert "skus" in data
    assert data["total"] == 4
    assert len(data["skus"]) == 4

    sku_ids = [s["id"] for s in data["skus"]]
    assert sku_ids == ["SKU-01", "SKU-02", "SKU-03", "SKU-04"]

    # Verify SKU-01 attributes
    sku_01 = next(s for s in data["skus"] if s["id"] == "SKU-01")
    assert sku_01["name"] == "Handcrafted Chanderi Silk Anarkali Kurta"
    assert sku_01["category"] == "Women's Ethnic"
    assert float(sku_01["price_inr"]) == 1899.00
    assert sku_01["fabric_stretch"] == "non_stretch"
    assert sku_01["has_shoulder"] is True
    assert sku_01["has_sleeve"] is True
    assert "sizes_json" in sku_01
    assert "M" in sku_01["sizes_json"]


@pytest.mark.asyncio
async def test_get_single_sku_success(async_client: AsyncClient) -> None:
    """Verify GET /v1/catalog/skus/{sku_id} returns single SKU details."""
    response = await async_client.get("/v1/catalog/skus/SKU-03")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == "SKU-03"
    assert data["name"] == "Raw Indigo Denim Trucker Jacket"
    assert float(data["price_inr"]) == 2499.00
    assert data["has_shoulder"] is True
    assert (
        data["has_sleeve"] is False
    )  # Intentionally missing sleeve measurement per ADR-004 & ADR-013
    assert data["provenance"] == "manual_fixture"


@pytest.mark.asyncio
async def test_get_non_existent_sku_returns_404(async_client: AsyncClient) -> None:
    """Verify GET /v1/catalog/skus/{sku_id} returns 404 for unknown SKU."""
    response = await async_client.get("/v1/catalog/skus/SKU-999")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()
