"""Deterministic Lifespan Database Seeding for ReturnZero AI.

Populates the 4 curated fashion SKUs and exactly 150 historical orders across
30 days using deterministic seeded RNG (random.Random(20261128)) per ADR-009,
ADR-013, AGENTS.md §5 (E9, E13) and PRE_EVENT_CHECKLIST.md §3.
All seeded orders have is_synthetic=True.
"""

from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.serviceable_pins import SYNTHETIC_SERVICEABLE_PINS, PinMetadata
from app.db.models import (
    DeliveryEventModel,
    FitLogModel,
    IncentiveInterventionModel,
    OrderModel,
    SkuModel,
)
from app.domain.sizing import CURATED_SKUS
from app.schemas.api_contracts import OrderOutcomeStatus

# Fixed reference timestamp for deterministic 30-day timeline
SEED_BASE_TIMESTAMP = datetime(2026, 11, 23, 12, 0, 0, tzinfo=UTC)
SEED_RNG_SEED = 20261128

# Realistic Indian customer persona fixtures
CUSTOMER_NAMES: list[str] = [
    "Aarav Sharma",
    "Priya Patel",
    "Rohan Mehta",
    "Ananya Iyer",
    "Vikram Singh",
    "Neha Gupta",
    "Rahul Verma",
    "Pooja Nair",
    "Aditya Joshi",
    "Meera Deshmukh",
    "Karan Malhotra",
    "Sneha Reddy",
    "Arjun Sen",
    "Ishita Roy",
    "Devendra Choudhary",
    "Kavita Yadav",
    "Gaurav Tiwari",
    "Ritu Singhania",
    "Manish Agarwal",
    "Simran Kaur",
]

STREET_TEMPLATES: list[str] = [
    "Flat 402, Sai Residency, near Hanuman Mandir",
    "House No. 12, Sector 15, opp SBI ATM",
    "Apartment 3B, Silver Oaks, behind City Mall",
    "Plot 88, Green Glen Layout, near Ganesh Temple",
    "Door 14/2, 3rd Cross, near Metro Pillar 124",
    "Bungalow 7, Shanti Nagar, opp Civil Hospital",
    "Flat 101, Krishna Enclave, near Railway Crossing",
    "House 45A, Model Town, near Central Market",
    "Room 12, Chawl No. 4, near Shiv Sena Shakha",
    "Villa 22, Palm Meadows, near Community Centre",
]


def _get_curated_sku_models() -> list[SkuModel]:
    """Generate the 4 canonical SKU entities matching fixtures and pitch deck."""
    sku_01_sizes = CURATED_SKUS["SKU-01"]["sizes"]
    sku_02_sizes = CURATED_SKUS["SKU-02"]["sizes"]
    sku_03_sizes = CURATED_SKUS["SKU-03"]["sizes"]
    sku_04_sizes = CURATED_SKUS["SKU-04"]["sizes"]

    return [
        SkuModel(
            id="SKU-01",
            name="Handcrafted Chanderi Silk Anarkali Kurta",
            category="Women's Ethnic",
            price_inr=Decimal("1899.00"),
            fabric_composition="100% Chanderi Silk, zero-stretch (0% elastane), structured bodice, 180 GSM",
            fabric_stretch="non_stretch",
            has_shoulder=True,
            has_sleeve=True,
            length_inches=48.0,
            sizes_json=sku_01_sizes,
            care_instructions="Dry clean only",
            provenance="manual_fixture",
            prompt_version="v1.0",
        ),
        SkuModel(
            id="SKU-02",
            name="Relaxed Mandarin Collar Linen Shirt",
            category="Men's Casual",
            price_inr=Decimal("1499.00"),
            fabric_composition="70% Cotton / 30% Linen, slight natural give, relaxed drape, 160 GSM",
            fabric_stretch="slight_stretch",
            has_shoulder=True,
            has_sleeve=True,
            length_inches=29.0,
            sizes_json=sku_02_sizes,
            care_instructions="Machine wash cold, tumble dry low",
            provenance="manual_fixture",
            prompt_version="v1.0",
        ),
        SkuModel(
            id="SKU-03",
            name="Raw Indigo Denim Trucker Jacket",
            category="Outerwear",
            price_inr=Decimal("2499.00"),
            fabric_composition="99% Cotton / 1% Spandex, 320 GSM, rigid armholes",
            fabric_stretch="non_stretch",
            has_shoulder=True,
            has_sleeve=False,  # Intentionally missing sleeve measurement per ADR-004 & ADR-013
            length_inches=26.0,
            sizes_json=sku_03_sizes,
            care_instructions="Hand wash cold, do not bleach",
            provenance="manual_fixture",
            prompt_version="v1.0",
        ),
        SkuModel(
            id="SKU-04",
            name="Flowy Floral Rayon Tiered Maxi Dress",
            category="Women's Western",
            price_inr=Decimal("1999.00"),
            fabric_composition="100% Viscose Rayon, highly fluid drape, elasticated smocked waist",
            fabric_stretch="slight_stretch",
            has_shoulder=True,
            has_sleeve=True,
            length_inches=53.0,
            sizes_json=sku_04_sizes,
            care_instructions="Gentle machine wash or hand wash",
            provenance="manual_fixture",
            prompt_version="v1.0",
        ),
    ]


async def seed_initial_data(session: AsyncSession) -> dict[str, int]:
    """Deterministically seed the 4 curated SKUs and 150 historical orders if empty.

    Follows PRE_EVENT_CHECKLIST.md §3 specifications:
    - 65% COD (98 orders) / 35% Prepaid (52 orders)
    - 40% Tier-1 Metro (~18% RTO)
    - 35% Tier-2 Cities (~30% RTO)
    - 25% Tier-3 Towns (~42% RTO)
    - All 6 outcome statuses populated
    - is_synthetic=True for all records
    - Strictly idempotent: returns existing row counts if table already populated.
    """
    # 1. Idempotency check: Count existing orders
    order_count_stmt = select(func.count()).select_from(OrderModel)
    existing_orders = (await session.execute(order_count_stmt)).scalar_one()

    sku_count_stmt = select(func.count()).select_from(SkuModel)
    existing_skus = (await session.execute(sku_count_stmt)).scalar_one()

    if existing_orders > 0 and existing_skus >= 4:
        return {"orders": existing_orders, "skus": existing_skus}

    # 2. Seed SKUs if needed
    if existing_skus < 4:
        for sku_model in _get_curated_sku_models():
            existing = (
                await session.execute(select(SkuModel).where(SkuModel.id == sku_model.id))
            ).scalar_one_or_none()
            if not existing:
                session.add(sku_model)
        await session.flush()

    if existing_orders > 0:
        return {"orders": existing_orders, "skus": 4}

    # 3. Deterministic 150 Historical Orders Generation
    rng = random.Random(SEED_RNG_SEED)

    # Filter pins by tier
    tier1_pins: list[tuple[str, PinMetadata]] = [
        (pin, meta) for pin, meta in SYNTHETIC_SERVICEABLE_PINS.items() if meta.tier == "Tier-1"
    ]
    tier2_pins: list[tuple[str, PinMetadata]] = [
        (pin, meta) for pin, meta in SYNTHETIC_SERVICEABLE_PINS.items() if meta.tier == "Tier-2"
    ]
    tier3_pins: list[tuple[str, PinMetadata]] = [
        (pin, meta) for pin, meta in SYNTHETIC_SERVICEABLE_PINS.items() if meta.tier == "Tier-3"
    ]

    # Pre-calculate counts:
    # Exactly 150 orders:
    # 60 Tier-1 (40%), 52 Tier-2 (34.67%), 38 Tier-3 (25.33%)
    # RTO targets:
    # Tier-1: 11 RTO (18.3%)
    # Tier-2: 16 RTO (30.8%)
    # Tier-3: 16 RTO (42.1%)
    # Total RTO: 43 orders
    # COD: exactly 98 orders (65.3%), Prepaid: exactly 52 orders (34.7%)

    sku_ids = ["SKU-01", "SKU-02", "SKU-03", "SKU-04"]
    sku_prices = {
        "SKU-01": Decimal("1899.00"),
        "SKU-02": Decimal("1499.00"),
        "SKU-03": Decimal("2499.00"),
        "SKU-04": Decimal("1999.00"),
    }
    sizes = ["S", "M", "L", "XL"]

    # Plan orders list with exact COD (98) and Prepaid (52) distributions
    # Tier-1 (60): 36 COD, 24 Prepaid -> 11 RTO (18.3%)
    # Tier-2 (52): 35 COD, 17 Prepaid -> 16 RTO (30.8%)
    # Tier-3 (38): 27 COD, 11 Prepaid -> 16 RTO (42.1%)
    tier_plans: list[dict[str, Any]] = [
        {
            "tier": "Tier-1",
            "pins": tier1_pins,
            "cod_rto": [
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
            ],  # 10
            "prepaid_rto": [
                OrderOutcomeStatus.PREPAID_RTO_RELOCATED.value,
            ],  # 1
            "cod_returns": [
                OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value,
                OrderOutcomeStatus.CUSTOMER_RETURNED_DEFECT.value,
            ],  # 2
            "prepaid_returns": [
                OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value,
                OrderOutcomeStatus.CUSTOMER_RETURNED_DEFECT.value,
            ],  # 2
            "cod_kept_count": 22,
            "prepaid_kept_count": 18,
            "cod_active": [
                OrderOutcomeStatus.PLACED.value,
                OrderOutcomeStatus.SAFE_FOR_DISPATCH.value,
            ],  # 2
            "prepaid_active": [
                OrderOutcomeStatus.ADDRESS_UPDATED.value,
                OrderOutcomeStatus.DELIVERY_RESCHEDULED.value,
                OrderOutcomeStatus.NDR.value,
            ],  # 3
        },
        {
            "tier": "Tier-2",
            "pins": tier2_pins,
            "cod_rto": [
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
            ],  # 15
            "prepaid_rto": [
                OrderOutcomeStatus.PREPAID_RTO_RELOCATED.value,
            ],  # 1
            "cod_returns": [
                OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value,
                OrderOutcomeStatus.CUSTOMER_RETURNED_DEFECT.value,
            ],  # 2
            "prepaid_returns": [
                OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value,
                OrderOutcomeStatus.CUSTOMER_RETURNED_DEFECT.value,
            ],  # 2
            "cod_kept_count": 16,
            "prepaid_kept_count": 13,
            "cod_active": [
                OrderOutcomeStatus.PLACED.value,
                OrderOutcomeStatus.SAFE_FOR_DISPATCH.value,
            ],  # 2
            "prepaid_active": [
                OrderOutcomeStatus.ADDRESS_UPDATED.value,
            ],  # 1
        },
        {
            "tier": "Tier-3",
            "pins": tier3_pins,
            "cod_rto": [
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_DOORSTEP_REFUSAL.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
                OrderOutcomeStatus.COD_RTO_ADDRESS_INCOMPLETE.value,
            ],  # 16
            "prepaid_rto": [],  # 0
            "cod_returns": [
                OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value,
                OrderOutcomeStatus.CUSTOMER_RETURNED_DEFECT.value,
            ],  # 2
            "prepaid_returns": [
                OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value,
                OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value,
            ],  # 2
            "cod_kept_count": 8,
            "prepaid_kept_count": 8,
            "cod_active": [
                OrderOutcomeStatus.DELIVERY_RESCHEDULED.value,
            ],  # 1
            "prepaid_active": [
                OrderOutcomeStatus.NDR.value,
            ],  # 1
        },
    ]

    orders_to_add: list[OrderModel] = []
    interventions_to_add: list[IncentiveInterventionModel] = []
    fit_logs_to_add: list[FitLogModel] = []
    delivery_events_to_add: list[DeliveryEventModel] = []

    order_idx = 1001

    for plan in tier_plans:
        tier_name: str = plan["tier"]
        pins_list = plan["pins"]

        # Build list of (payment_method, order_status) tuples
        tier_orders_spec: list[tuple[str, str]] = []

        # COD items
        for st in plan["cod_rto"]:
            tier_orders_spec.append(("COD", st))
        for st in plan["cod_returns"]:
            tier_orders_spec.append(("COD", st))
        for _ in range(plan["cod_kept_count"]):
            tier_orders_spec.append(("COD", OrderOutcomeStatus.DELIVERED_KEPT.value))
        for st in plan["cod_active"]:
            tier_orders_spec.append(("COD", st))

        # Prepaid items
        for st in plan["prepaid_rto"]:
            tier_orders_spec.append(("Prepaid", st))
        for st in plan["prepaid_returns"]:
            tier_orders_spec.append(("Prepaid", st))
        for _ in range(plan["prepaid_kept_count"]):
            tier_orders_spec.append(("Prepaid", OrderOutcomeStatus.DELIVERED_KEPT.value))
        for st in plan["prepaid_active"]:
            tier_orders_spec.append(("Prepaid", st))

        # Deterministic shuffle within the tier
        rng.shuffle(tier_orders_spec)

        for payment_method, status in tier_orders_spec:
            order_id = f"RZ-{order_idx}"
            order_number = f"RZ-{order_idx}"
            order_idx += 1

            pin, pin_meta = rng.choice(pins_list)
            customer_name = rng.choice(CUSTOMER_NAMES)
            phone = f"+91 9{rng.randint(100000000, 999999999)}"
            street = rng.choice(STREET_TEMPLATES)

            sku_id = rng.choice(sku_ids)
            # Make SKU-03 slightly more prone to fit returns
            if status == OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value and rng.random() < 0.6:
                sku_id = "SKU-03"

            selected_size = rng.choice(sizes)
            base_price = sku_prices[sku_id]

            # Fit check usage: ~60%
            used_fit = rng.random() < 0.60
            if status == OrderOutcomeStatus.CUSTOMER_RETURNED_FIT.value:
                used_fit = False  # shoppers with fit returns mostly skipped fit check

            # Timestamp: spread across past 30 days
            active_statuses = [
                OrderOutcomeStatus.PLACED.value,
                OrderOutcomeStatus.SAFE_FOR_DISPATCH.value,
                OrderOutcomeStatus.ADDRESS_UPDATED.value,
                OrderOutcomeStatus.DELIVERY_RESCHEDULED.value,
                OrderOutcomeStatus.NDR.value,
            ]
            if status in active_statuses:
                hours_ago = rng.uniform(2.0, 48.0)
            else:
                hours_ago = rng.uniform(48.0, 720.0)

            created_at = SEED_BASE_TIMESTAMP - timedelta(hours=hours_ago)

            # Risk score based on tier and payment
            if payment_method == "COD":
                risk_score = rng.randint(35, 75) if pin_meta.is_high_risk else rng.randint(20, 50)
            else:
                risk_score = rng.randint(5, 25)

            # Incentive intervention
            discount_applied = Decimal("0.00")
            if payment_method == "COD" and risk_score >= 35 and rng.random() < 0.35:
                # Converted to UPI via incentive
                intervention_id = str(uuid.uuid4())
                interventions_to_add.append(
                    IncentiveInterventionModel(
                        id=intervention_id,
                        order_id=order_id,
                        original_payment="COD",
                        offered_discount_inr=Decimal("40.00"),
                        converted_to_upi=True,
                        expected_savings_inr=Decimal("48.00"),
                        retained_headroom_inr=Decimal("8.00"),
                        reason_code="REASON_ELEVATED_RISK_CONVERTIBLE",
                        created_at=created_at,
                    )
                )
                discount_applied = Decimal("40.00")
            elif payment_method == "COD" and risk_score >= 35:
                # Offered but not converted
                intervention_id = str(uuid.uuid4())
                interventions_to_add.append(
                    IncentiveInterventionModel(
                        id=intervention_id,
                        order_id=order_id,
                        original_payment="COD",
                        offered_discount_inr=Decimal("40.00"),
                        converted_to_upi=False,
                        expected_savings_inr=Decimal("48.00"),
                        retained_headroom_inr=Decimal("8.00"),
                        reason_code="REASON_ELEVATED_RISK_CONVERTIBLE",
                        created_at=created_at,
                    )
                )

            total_inr = base_price - discount_applied

            order_model = OrderModel(
                id=order_id,
                order_number=order_number,
                customer_name=customer_name,
                customer_phone=phone,
                street_address=street,
                city=pin_meta.city,
                state=pin_meta.state,
                pin_code=pin,
                tier=tier_name,
                address_status="Complete"
                if "near" in street.lower() or "opp" in street.lower()
                else "NeedsLandmark",
                payment_method=payment_method,
                order_status=status,
                total_inr=total_inr,
                cod_risk_score=risk_score,
                discount_applied_inr=discount_applied,
                selected_size=selected_size,
                sku_id=sku_id,
                used_fit_check=used_fit,
                consent_status="opted_in",
                dispatch_priority="priority" if discount_applied > 0 else "standard",
                is_synthetic=True,
                created_at=created_at,
            )
            orders_to_add.append(order_model)

            # Fit log if shopper used fit check
            if used_fit:
                fit_log_id = str(uuid.uuid4())
                fit_logs_to_add.append(
                    FitLogModel(
                        id=fit_log_id,
                        sku_id=sku_id,
                        order_id=order_id,
                        known_brand=rng.choice(["Zara", "H&M", "Uniqlo"]),
                        known_size=selected_size,
                        recommended_size=selected_size,
                        confidence_level="Medium" if sku_id == "SKU-03" else "High",
                        fit_score=rng.randint(82, 94),
                        is_correct=True
                        if status == OrderOutcomeStatus.DELIVERED_KEPT.value
                        else None,
                        created_at=created_at - timedelta(minutes=rng.randint(5, 20)),
                    )
                )

            # Delivery Events
            if status == OrderOutcomeStatus.DELIVERED_KEPT.value:
                delivery_events_to_add.append(
                    DeliveryEventModel(
                        id=str(uuid.uuid4()),
                        order_id=order_id,
                        event_type="Dispatched",
                        reason=None,
                        timestamp=created_at + timedelta(hours=12),
                    )
                )
                delivery_events_to_add.append(
                    DeliveryEventModel(
                        id=str(uuid.uuid4()),
                        order_id=order_id,
                        event_type="OutForDelivery",
                        reason=None,
                        timestamp=created_at + timedelta(hours=36),
                    )
                )
                delivery_events_to_add.append(
                    DeliveryEventModel(
                        id=str(uuid.uuid4()),
                        order_id=order_id,
                        event_type="Delivered",
                        reason="Customer accepted at doorstep",
                        timestamp=created_at + timedelta(hours=42),
                    )
                )
            elif "RTO" in status:
                delivery_events_to_add.append(
                    DeliveryEventModel(
                        id=str(uuid.uuid4()),
                        order_id=order_id,
                        event_type="Dispatched",
                        reason=None,
                        timestamp=created_at + timedelta(hours=12),
                    )
                )
                delivery_events_to_add.append(
                    DeliveryEventModel(
                        id=str(uuid.uuid4()),
                        order_id=order_id,
                        event_type="OutForDelivery",
                        reason=None,
                        timestamp=created_at + timedelta(hours=48),
                    )
                )
                delivery_events_to_add.append(
                    DeliveryEventModel(
                        id=str(uuid.uuid4()),
                        order_id=order_id,
                        event_type="Refused" if "Doorstep Refusal" in status else "NDR",
                        reason=status,
                        timestamp=created_at + timedelta(hours=54),
                    )
                )

    # 4. Insert orders and related records
    session.add_all(orders_to_add)
    session.add_all(interventions_to_add)
    session.add_all(fit_logs_to_add)
    session.add_all(delivery_events_to_add)
    await session.flush()

    return {"orders": len(orders_to_add), "skus": 4}
