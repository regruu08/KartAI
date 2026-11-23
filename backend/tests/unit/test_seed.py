"""Unit tests for deterministic lifespan database seeding.

Verifies seed distribution requirements from PRE_EVENT_CHECKLIST.md §3:
- Exactly 150 orders across past 30 days
- 4 curated SKUs
- 65% COD (98 orders) / 35% Prepaid (52 orders)
- 40% Tier-1 Metro (~18% RTO)
- 35% Tier-2 Cities (~30% RTO)
- 25% Tier-3 Towns (~42% RTO)
- All 6 outcome statuses populated
- All rows marked is_synthetic=True
- Strictly idempotent on subsequent executions
"""

from __future__ import annotations

from datetime import UTC

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    DeliveryEventModel,
    FitLogModel,
    IncentiveInterventionModel,
    OrderModel,
    SkuModel,
)
from app.db.seed import seed_initial_data
from app.db.session import reset_db


@pytest.mark.asyncio
async def test_seed_initial_data_idempotency(db_session: AsyncSession) -> None:
    """Verify seed execution is idempotent and does not create duplicate records."""
    await reset_db()

    # First seeding run
    result1 = await seed_initial_data(db_session)
    assert result1["orders"] == 150
    assert result1["skus"] == 4

    # Second seeding run should return existing counts immediately without inserts
    result2 = await seed_initial_data(db_session)
    assert result2["orders"] == 150
    assert result2["skus"] == 4

    # Verify database counts
    order_count = (
        await db_session.execute(select(func.count()).select_from(OrderModel))
    ).scalar_one()
    sku_count = (await db_session.execute(select(func.count()).select_from(SkuModel))).scalar_one()
    assert order_count == 150
    assert sku_count == 4


@pytest.mark.asyncio
async def test_seed_payment_distribution(db_session: AsyncSession) -> None:
    """Verify payment method split is exactly 65% COD (98) and 35% Prepaid (52)."""
    cod_stmt = (
        select(func.count()).select_from(OrderModel).where(OrderModel.payment_method == "COD")
    )
    cod_count = (await db_session.execute(cod_stmt)).scalar_one()

    prepaid_stmt = (
        select(func.count()).select_from(OrderModel).where(OrderModel.payment_method == "Prepaid")
    )
    prepaid_count = (await db_session.execute(prepaid_stmt)).scalar_one()

    assert cod_count == 98
    assert prepaid_count == 52
    assert cod_count + prepaid_count == 150


@pytest.mark.asyncio
async def test_seed_tier_distribution_and_rto_rates(db_session: AsyncSession) -> None:
    """Verify tier volume shares and respective RTO percentages."""
    # Tier-1: 60 orders (40%), ~18% RTO (11)
    t1_total = (
        await db_session.execute(
            select(func.count()).select_from(OrderModel).where(OrderModel.tier == "Tier-1")
        )
    ).scalar_one()
    t1_rto = (
        await db_session.execute(
            select(func.count())
            .select_from(OrderModel)
            .where(OrderModel.tier == "Tier-1", OrderModel.order_status.like("%RTO%"))
        )
    ).scalar_one()

    assert t1_total == 60
    assert t1_rto == 11
    assert round(t1_rto / t1_total * 100.0, 1) == 18.3

    # Tier-2: 52 orders (35%), ~30% RTO (16)
    t2_total = (
        await db_session.execute(
            select(func.count()).select_from(OrderModel).where(OrderModel.tier == "Tier-2")
        )
    ).scalar_one()
    t2_rto = (
        await db_session.execute(
            select(func.count())
            .select_from(OrderModel)
            .where(OrderModel.tier == "Tier-2", OrderModel.order_status.like("%RTO%"))
        )
    ).scalar_one()

    assert t2_total == 52
    assert t2_rto == 16
    assert round(t2_rto / t2_total * 100.0, 1) == 30.8

    # Tier-3: 38 orders (25%), ~42% RTO (16)
    t3_total = (
        await db_session.execute(
            select(func.count()).select_from(OrderModel).where(OrderModel.tier == "Tier-3")
        )
    ).scalar_one()
    t3_rto = (
        await db_session.execute(
            select(func.count())
            .select_from(OrderModel)
            .where(OrderModel.tier == "Tier-3", OrderModel.order_status.like("%RTO%"))
        )
    ).scalar_one()

    assert t3_total == 38
    assert t3_rto == 16
    assert round(t3_rto / t3_total * 100.0, 1) == 42.1

    assert t1_total + t2_total + t3_total == 150
    assert t1_rto + t2_rto + t3_rto == 43


@pytest.mark.asyncio
async def test_seed_outcome_statuses_represented(db_session: AsyncSession) -> None:
    """Verify all 6 core outcome statuses from PRE_EVENT_CHECKLIST.md are present."""
    expected_outcomes = [
        "Delivered (Kept)",
        "Customer Returned (Fit Issue)",
        "Customer Returned (Defect)",
        "COD RTO (Doorstep Refusal)",
        "COD RTO (Address Incomplete)",
        "Prepaid RTO (Customer Relocated)",
    ]

    for status_label in expected_outcomes:
        count = (
            await db_session.execute(
                select(func.count())
                .select_from(OrderModel)
                .where(OrderModel.order_status == status_label)
            )
        ).scalar_one()
        assert count > 0, f"Expected outcome '{status_label}' to be present in seed dataset"


@pytest.mark.asyncio
async def test_seed_synthetic_flag_and_timestamps(db_session: AsyncSession) -> None:
    """Verify all seeded orders have is_synthetic=True and timestamps span past 30 days."""
    non_synthetic = (
        await db_session.execute(
            select(func.count()).select_from(OrderModel).where(OrderModel.is_synthetic.is_(False))
        )
    ).scalar_one()
    assert non_synthetic == 0, "All seeded orders must be synthetic per ADR-009"

    # Verify timestamps are in UTC and within past 31 days
    min_created = (await db_session.execute(select(func.min(OrderModel.created_at)))).scalar_one()
    max_created = (await db_session.execute(select(func.max(OrderModel.created_at)))).scalar_one()

    assert min_created is not None
    assert max_created is not None
    if min_created.tzinfo is not None:
        assert min_created.tzinfo == UTC
    if max_created.tzinfo is not None:
        assert max_created.tzinfo == UTC

    delta = max_created - min_created
    assert delta.total_seconds() > 0
    assert delta.days <= 31


@pytest.mark.asyncio
async def test_seed_related_entities_populated(db_session: AsyncSession) -> None:
    """Verify FitLogModel, IncentiveInterventionModel, and DeliveryEventModel are populated."""
    fit_logs_count = (
        await db_session.execute(select(func.count()).select_from(FitLogModel))
    ).scalar_one()
    interventions_count = (
        await db_session.execute(select(func.count()).select_from(IncentiveInterventionModel))
    ).scalar_one()
    events_count = (
        await db_session.execute(select(func.count()).select_from(DeliveryEventModel))
    ).scalar_one()

    assert fit_logs_count > 50
    assert interventions_count > 20
    assert events_count > 100
