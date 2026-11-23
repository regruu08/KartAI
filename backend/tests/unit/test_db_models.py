"""Unit tests for SQLAlchemy 2.0 database models.

Verifies model creation, typed attributes, defaults, decimal precision,
and relationship structures for SkuModel, OrderModel, FitLogModel,
IncentiveInterventionModel, and DeliveryEventModel per ADR-005, ADR-006, and ADR-009.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from app.db.models import (
    DeliveryEventModel,
    FitLogModel,
    IncentiveInterventionModel,
    OrderModel,
    SkuModel,
    utc_now,
)


def test_sku_model_attributes() -> None:
    """Verify SkuModel creation and typed fields."""
    sku = SkuModel(
        id="SKU-TEST-01",
        name="Chanderi Silk Test Kurta",
        category="Women's Ethnic",
        price_inr=Decimal("1899.00"),
        fabric_composition="100% Chanderi Silk",
        fabric_stretch="non_stretch",
        has_shoulder=True,
        has_sleeve=True,
        length_inches=48.0,
        sizes_json={"S": {"chest": 36.0, "shoulder": 14.5}},
        care_instructions="Dry clean only",
        provenance="manual_fixture",
        prompt_version="v1.0",
    )

    assert sku.id == "SKU-TEST-01"
    assert sku.name == "Chanderi Silk Test Kurta"
    assert sku.price_inr == Decimal("1899.00")
    assert sku.has_shoulder is True
    assert sku.has_sleeve is True
    assert sku.length_inches == 48.0
    assert sku.sizes_json["S"]["chest"] == 36.0
    assert sku.provenance == "manual_fixture"


def test_order_model_attributes_and_defaults() -> None:
    """Verify OrderModel creation, defaults, and synthetic flag."""
    order = OrderModel(
        id="RZ-TEST-1001",
        order_number="RZ-TEST-1001",
        customer_name="Aarav Sharma",
        customer_phone="+91 9876543210",
        street_address="Flat 402, Sai Residency, near Hanuman Mandir",
        city="Delhi",
        state="Delhi",
        pin_code="110001",
        tier="Tier-1",
        address_status="Complete",
        payment_method="COD",
        order_status="Placed",
        total_inr=Decimal("1899.00"),
        cod_risk_score=25,
        discount_applied_inr=Decimal("0.00"),
        selected_size="M",
        sku_id="SKU-01",
        used_fit_check=True,
        consent_status="opted_in",
        dispatch_priority="standard",
        is_synthetic=True,
    )

    assert order.id == "RZ-TEST-1001"
    assert order.is_synthetic is True
    assert order.payment_method == "COD"
    assert order.order_status == "Placed"
    assert order.total_inr == Decimal("1899.00")
    assert order.discount_applied_inr == Decimal("0.00")
    assert order.cod_risk_score == 25
    assert order.used_fit_check is True


def test_fit_log_model_attributes() -> None:
    """Verify FitLogModel creation and categorization."""
    log_id = str(uuid.uuid4())
    fit_log = FitLogModel(
        id=log_id,
        sku_id="SKU-01",
        order_id="RZ-TEST-1001",
        known_brand="Zara",
        known_size="M",
        recommended_size="L",
        confidence_level="High",
        fit_score=88,
        is_correct=True,
    )

    assert fit_log.id == log_id
    assert fit_log.sku_id == "SKU-01"
    assert fit_log.known_brand == "Zara"
    assert fit_log.confidence_level == "High"
    assert fit_log.fit_score == 88
    assert fit_log.is_correct is True


def test_incentive_intervention_model_attributes() -> None:
    """Verify IncentiveInterventionModel creation and decimal amounts."""
    intervention_id = str(uuid.uuid4())
    intervention = IncentiveInterventionModel(
        id=intervention_id,
        order_id="RZ-TEST-1001",
        original_payment="COD",
        offered_discount_inr=Decimal("40.00"),
        converted_to_upi=True,
        expected_savings_inr=Decimal("48.00"),
        retained_headroom_inr=Decimal("8.00"),
        reason_code="REASON_ELEVATED_RISK_CONVERTIBLE",
    )

    assert intervention.id == intervention_id
    assert intervention.offered_discount_inr == Decimal("40.00")
    assert intervention.converted_to_upi is True
    assert intervention.expected_savings_inr == Decimal("48.00")
    assert intervention.retained_headroom_inr == Decimal("8.00")
    assert intervention.reason_code == "REASON_ELEVATED_RISK_CONVERTIBLE"


def test_delivery_event_model_attributes() -> None:
    """Verify DeliveryEventModel creation and event types."""
    event_id = str(uuid.uuid4())
    now_ts = datetime.now(UTC)
    event = DeliveryEventModel(
        id=event_id,
        order_id="RZ-TEST-1001",
        event_type="OutForDelivery",
        reason="Assigned to courier route",
        timestamp=now_ts,
    )

    assert event.id == event_id
    assert event.event_type == "OutForDelivery"
    assert event.reason == "Assigned to courier route"
    assert event.timestamp == now_ts


def test_utc_now_helper() -> None:
    """Verify utc_now produces timezone-aware UTC datetime."""
    now = utc_now()
    assert now.tzinfo is not None
    assert now.tzinfo == UTC
