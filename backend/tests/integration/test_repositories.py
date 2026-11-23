"""Integration tests for Asynchronous Database Repositories.

Verifies async CRUD and transaction behavior for SkuRepository, OrderRepository,
FitLogRepository, IncentiveRepository, DeliveryEventRepository, and AnalyticsRepository.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    DeliveryEventModel,
    FitLogModel,
    IncentiveInterventionModel,
    OrderModel,
)
from app.db.repositories import (
    AnalyticsRepository,
    DeliveryEventRepository,
    FitLogRepository,
    IncentiveRepository,
    OrderRepository,
    SkuRepository,
)


@pytest.mark.asyncio
async def test_sku_repository_crud(db_session: AsyncSession) -> None:
    """Verify SkuRepository get, list, create, and upsert."""
    repo = SkuRepository(db_session)

    # List seeded SKUs
    skus = await repo.list_all()
    assert len(skus) >= 4
    sku_ids = [s.id for s in skus]
    assert "SKU-01" in sku_ids
    assert "SKU-03" in sku_ids

    # Get by ID
    sku_01 = await repo.get_by_id("SKU-01")
    assert sku_01 is not None
    assert sku_01.name == "Handcrafted Chanderi Silk Anarkali Kurta"
    assert sku_01.price_inr == Decimal("1899.00")

    # Upsert existing SKU (e.g. updating extraction provenance)
    sku_01.provenance = "live_gemini"
    sku_01.extracted_at = datetime.now(UTC)
    updated = await repo.upsert(sku_01)
    assert updated.provenance == "live_gemini"
    assert updated.extracted_at is not None

    # Get non-existent
    non_existent = await repo.get_by_id("SKU-DOES-NOT-EXIST")
    assert non_existent is None


@pytest.mark.asyncio
async def test_order_repository_crud_and_status_update(db_session: AsyncSession) -> None:
    """Verify OrderRepository retrieval, creation, counting, and status mutation."""
    repo = OrderRepository(db_session)

    # Count orders
    count = await repo.count_orders()
    assert count >= 150

    # Get by ID and order_number
    order = await repo.get_by_id("RZ-1001")
    assert order is not None
    assert order.order_number == "RZ-1001"

    order_by_num = await repo.get_by_order_number("RZ-1001")
    assert order_by_num is not None
    assert order_by_num.id == "RZ-1001"

    # List orders with pagination
    page1 = await repo.list_orders(limit=10, offset=0)
    assert len(page1) == 10

    # Create new order
    new_order = OrderModel(
        id="RZ-TEST-REPO-01",
        order_number="RZ-TEST-REPO-01",
        customer_name="Test Shopper",
        customer_phone="+91 9999999999",
        street_address="House 1, Street 2, near Test Landmark",
        city="Delhi",
        state="Delhi",
        pin_code="110001",
        tier="Tier-1",
        address_status="Complete",
        payment_method="COD",
        order_status="Placed",
        total_inr=Decimal("1899.00"),
        cod_risk_score=20,
        discount_applied_inr=Decimal("0.00"),
        selected_size="M",
        sku_id="SKU-01",
        used_fit_check=True,
        consent_status="opted_in",
        dispatch_priority="standard",
        is_synthetic=True,
    )
    created = await repo.create(new_order)
    assert created.id == "RZ-TEST-REPO-01"

    # Update status
    updated = await repo.update_status(
        "RZ-TEST-REPO-01",
        status="Safe_For_Dispatch",
        address_status="Address_Updated",
    )
    assert updated is not None
    assert updated.order_status == "Safe_For_Dispatch"
    assert updated.address_status == "Address_Updated"

    # Update status for non-existent order
    none_order = await repo.update_status("RZ-NON-EXISTENT", status="Cancelled")
    assert none_order is None


@pytest.mark.asyncio
async def test_fit_log_repository(db_session: AsyncSession) -> None:
    """Verify FitLogRepository creation and retrieval."""
    repo = FitLogRepository(db_session)
    log_id = str(uuid.uuid4())

    new_log = FitLogModel(
        id=log_id,
        sku_id="SKU-02",
        order_id=None,
        known_brand="H&M",
        known_size="M",
        recommended_size="M",
        confidence_level="High",
        fit_score=92,
        is_correct=None,
    )
    created = await repo.create(new_log)
    assert created.id == log_id

    fetched = await repo.get_by_id(log_id)
    assert fetched is not None
    assert fetched.known_brand == "H&M"
    assert fetched.recommended_size == "M"

    logs_for_sku = await repo.list_by_sku("SKU-02")
    assert len(logs_for_sku) > 0


@pytest.mark.asyncio
async def test_incentive_repository(db_session: AsyncSession) -> None:
    """Verify IncentiveRepository creation and order binding."""
    repo = IncentiveRepository(db_session)
    int_id = str(uuid.uuid4())

    intervention = IncentiveInterventionModel(
        id=int_id,
        order_id="RZ-1001",
        original_payment="COD",
        offered_discount_inr=Decimal("40.00"),
        converted_to_upi=True,
        expected_savings_inr=Decimal("48.00"),
        retained_headroom_inr=Decimal("8.00"),
        reason_code="REASON_ELEVATED_RISK_CONVERTIBLE",
    )
    created = await repo.create(intervention)
    assert created.id == int_id

    by_order = await repo.get_by_order_id("RZ-1001")
    assert len(by_order) >= 1
    assert any(i.id == int_id for i in by_order)


@pytest.mark.asyncio
async def test_delivery_event_repository(db_session: AsyncSession) -> None:
    """Verify DeliveryEventRepository event chronological logging."""
    repo = DeliveryEventRepository(db_session)
    event_id = str(uuid.uuid4())

    event = DeliveryEventModel(
        id=event_id,
        order_id="RZ-1001",
        event_type="NDR_Resolved",
        reason="Customer rescheduled morning slot",
    )
    created = await repo.create(event)
    assert created.id == event_id

    events = await repo.list_by_order_id("RZ-1001")
    assert len(events) >= 1
    assert any(e.id == event_id for e in events)


@pytest.mark.asyncio
async def test_analytics_repository_live_overview(db_session: AsyncSession) -> None:
    """Verify AnalyticsRepository SQL aggregation consistency."""
    repo = AnalyticsRepository(db_session)
    overview = await repo.get_live_overview()

    assert overview.total_orders >= 150
    assert overview.cod_orders_count > 0
    assert overview.prepaid_orders_count > 0
    assert overview.cod_orders_count + overview.prepaid_orders_count == overview.total_orders

    assert overview.rto_count > 0
    assert overview.rto_rate_pct > 0.0

    # Verify RTO and Customer Return metrics are strictly separated
    assert overview.customer_return_count > 0
    assert overview.customer_return_rate_pct > 0.0

    # Verify tier and SKU breakdowns
    assert len(overview.tier_breakdown) == 3
    tier_names = {t.tier for t in overview.tier_breakdown}
    assert tier_names == {"Tier-1", "Tier-2", "Tier-3"}

    assert len(overview.sku_breakdown) == 4
    sku_ids = {s.sku_id for s in overview.sku_breakdown}
    assert sku_ids == {"SKU-01", "SKU-02", "SKU-03", "SKU-04"}

    # SKU-03 must flag missing measurements
    sku_03_stat = next(s for s in overview.sku_breakdown if s.sku_id == "SKU-03")
    assert sku_03_stat.has_missing_measurements is True
    assert sku_03_stat.alert_message is not None

    # Binding disclaimer attribution
    assert "modelled direct operating savings" in overview.disclaimer
