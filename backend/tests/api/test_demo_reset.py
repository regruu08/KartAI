"""API tests for /v1/demo/reset endpoint.

Verifies guarded administrative reset endpoint security:
- 403 on missing or invalid token
- 403 when demo mode is disabled
- 200 on valid token restoring database to pristine 150-order state
Reference: ADR-009, AGENTS.md §6.5 & §7.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models import OrderModel
from app.db.repositories import OrderRepository
from app.main import create_app

VALID_DEMO_TOKEN = "returnzero-demo-secret-2026"


@pytest.mark.asyncio
async def test_demo_reset_missing_token_returns_403(async_client: AsyncClient) -> None:
    """Verify POST /v1/demo/reset returns 403 if X-Demo-Token header is omitted."""
    response = await async_client.post("/v1/demo/reset")
    assert response.status_code == 403
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_demo_reset_invalid_token_returns_403(async_client: AsyncClient) -> None:
    """Verify POST /v1/demo/reset returns 403 if token does not match."""
    headers = {"X-Demo-Token": "invalid-token-attempt"}
    response = await async_client.post("/v1/demo/reset", headers=headers)
    assert response.status_code == 403
    assert "Invalid or missing" in response.json()["detail"]


@pytest.mark.asyncio
async def test_demo_reset_when_demo_mode_disabled() -> None:
    """Verify POST /v1/demo/reset returns 403 when DEMO_MODE is False."""
    prod_settings = Settings(
        ENVIRONMENT="production",
        DEMO_MODE=False,
        DEMO_TOKEN=SecretStr(VALID_DEMO_TOKEN),
    )
    from app.config import get_settings

    app = create_app(prod_settings)
    app.dependency_overrides[get_settings] = lambda: prod_settings
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            headers = {"X-Demo-Token": VALID_DEMO_TOKEN}
            response = await client.post("/v1/demo/reset", headers=headers)
            assert response.status_code == 403
            assert "disabled" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_demo_reset_valid_token_restores_150_orders(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verify POST /v1/demo/reset restores database to pristine 150-order state."""
    # 1. Mutate database: add a 151st order
    order_repo = OrderRepository(db_session)
    extra_order = OrderModel(
        id="RZ-9999",
        order_number="RZ-9999",
        customer_name="Temporary Mutation",
        customer_phone="+91 9999999999",
        street_address="Temporary Address",
        city="Mumbai",
        state="Maharashtra",
        pin_code="400001",
        tier="Tier-1",
        address_status="Complete",
        payment_method="COD",
        order_status="Placed",
        total_inr=Decimal("1899.00"),
        cod_risk_score=15,
        discount_applied_inr=Decimal("0.00"),
        selected_size="M",
        sku_id="SKU-01",
        used_fit_check=False,
        consent_status="opted_in",
        dispatch_priority="standard",
        is_synthetic=True,
    )
    await order_repo.create(extra_order)
    await db_session.commit()

    count_before = (
        await db_session.execute(select(func.count()).select_from(OrderModel))
    ).scalar_one()
    assert count_before >= 151

    # 2. Call reset endpoint with valid token
    headers = {"X-Demo-Token": VALID_DEMO_TOKEN}
    response = await async_client.post("/v1/demo/reset", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["seeded_orders"] == 150
    assert data["seeded_skus"] == 4
    assert "pristine 150-order" in data["message"]

    # 3. Verify order count is restored to exactly 150
    count_after = (
        await db_session.execute(select(func.count()).select_from(OrderModel))
    ).scalar_one()
    assert count_after == 150

    # 4. Verify temporary order is gone
    extra_order_check = await order_repo.get_by_id("RZ-9999")
    assert extra_order_check is None
