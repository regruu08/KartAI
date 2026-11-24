"""Contract tests for ReturnZero AI API per AGENTS.md §7.

Permanently verifies that every canonical endpoint defined in the specification
is registered in OpenAPI with the expected HTTP method and path.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.main import create_app

# Canonical contract endpoints from AGENTS.md §7
CANONICAL_API_ENDPOINTS: list[tuple[str, str]] = [
    ("GET", "/healthz"),
    ("GET", "/v1/catalog/skus"),
    ("GET", "/v1/catalog/skus/{sku_id}"),
    ("POST", "/v1/catalog/skus/{sku_id}/extract"),
    ("POST", "/v1/fit/recommend"),
    ("POST", "/v1/risk/evaluate"),
    ("POST", "/v1/incentive/quote"),
    ("POST", "/v1/orders"),
    ("GET", "/v1/orders"),
    ("GET", "/v1/orders/{order_id}"),
    ("POST", "/v1/orders/{order_id}/verify"),
    ("POST", "/v1/orders/{order_id}/ndr"),
    ("GET", "/v1/analytics/overview"),
    ("GET", "/v1/analytics/scenario"),
    ("POST", "/v1/demo/reset"),
]


def test_canonical_api_endpoints_registered_in_openapi() -> None:
    """Assert all canonical endpoints from AGENTS.md §7 are present in OpenAPI schema."""
    app: FastAPI = create_app()
    openapi_schema = app.openapi()
    paths = openapi_schema.get("paths", {})

    missing_endpoints: list[str] = []
    for method, path in CANONICAL_API_ENDPOINTS:
        method_lower = method.lower()
        if path not in paths or method_lower not in paths[path]:
            missing_endpoints.append(f"{method} {path}")

    assert not missing_endpoints, f"Missing canonical endpoints in OpenAPI: {missing_endpoints}"


@pytest.mark.asyncio
async def test_canonical_fit_recommend_persists_fit_log(async_client: AsyncClient) -> None:
    """Assert POST /v1/fit/recommend returns sizing and persists a FitLogModel row."""
    payload = {
        "sku_id": "SKU-01",
        "known_brand": "Zara",
        "known_size": "M",
        "fit_preference": "tailored",
        "height_cm": 165.0,
    }
    response = await async_client.post("/v1/fit/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sku_id"] == "SKU-01"
    assert data["recommended_size"] == "L"
