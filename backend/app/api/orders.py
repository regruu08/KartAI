"""Customer Order Management and Delivery Assurance API Endpoints.

Provides order lifecycle operations: checkout creation, retrieval, landmark verification,
and NDR reschedule coordination.
Reference: ADR-003, ADR-005, ADR-015, AGENTS.md §5 (E3, E15) & §7.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.serviceable_pins import get_pin_metadata
from app.db.models import DeliveryEventModel, FitLogModel, IncentiveInterventionModel, OrderModel
from app.db.repositories import OrderRepository, SkuRepository
from app.db.session import get_db_session
from app.domain.address import address_quality
from app.domain.risk import evaluate_order_risk
from app.domain.sizing import recommend_size
from app.integrations.gemini.normalizer import AddressNormalizer
from app.schemas.api_contracts import (
    OrderCreateRequest,
    OrderListResponse,
    OrderNdrRequest,
    OrderResponse,
    OrderVerifyRequest,
)

router = APIRouter()


def _model_to_response(order: OrderModel) -> OrderResponse:
    """Map SQLAlchemy OrderModel to Pydantic OrderResponse."""
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer_name=order.customer_name,
        street_address=order.street_address,
        pin_code=order.pin_code,
        city=order.city,
        state=order.state,
        tier=order.tier,
        payment_method=order.payment_method,
        total_inr=order.total_inr,
        discount_applied_inr=order.discount_applied_inr,
        selected_size=order.selected_size,
        sku_id=order.sku_id,
        cod_risk_score=order.cod_risk_score,
        order_status=order.order_status,
        address_status=order.address_status,
        used_fit_check=order.used_fit_check,
        consent_status=order.consent_status,
        dispatch_priority=order.dispatch_priority,
        is_synthetic=order.is_synthetic,
        created_at=order.created_at,
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create customer order",
    description="Persist new order from checkout flow with risk evaluation and optional fit audit log.",
    tags=["Orders"],
)
async def create_order(
    request: OrderCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> OrderResponse:
    """Create a new customer order."""
    sku_repo = SkuRepository(session)
    sku = await sku_repo.get_by_id(request.sku_id)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU '{request.sku_id}' not found in catalog",
        )

    order_id = f"ord_{uuid.uuid4().hex[:12]}"
    date_prefix = datetime.now(UTC).strftime("%Y%m%d")
    short_suffix = uuid.uuid4().hex[:6].upper()
    order_number = f"ORD-{date_prefix}-{short_suffix}"

    pin_meta = get_pin_metadata(request.pin_code)
    tier = pin_meta.tier if pin_meta else "Tier-2"
    city = pin_meta.city if (pin_meta and not request.city) else request.city
    state = pin_meta.state if (pin_meta and not request.state) else request.state

    addr_eval = address_quality(request.street_address, request.pin_code)
    risk_result = evaluate_order_risk(
        payment_method=request.payment_method,
        street_address=request.street_address,
        pin_code=request.pin_code,
        has_used_fit_twin=request.has_used_fit_twin,
        is_bracketing=request.is_bracketing,
    )

    item_price = sku.price_inr
    subtotal = item_price * request.quantity
    total_inr = max(Decimal("0.00"), subtotal - request.applied_discount_inr)
    dispatch_priority = "priority" if request.payment_method.upper() == "PREPAID" else "standard"

    order = OrderModel(
        id=order_id,
        order_number=order_number,
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        street_address=request.street_address,
        city=city,
        state=state,
        pin_code=request.pin_code,
        tier=tier,
        address_status=addr_eval.status,
        payment_method=request.payment_method.upper(),
        order_status="Placed",
        total_inr=total_inr,
        cod_risk_score=risk_result.risk_score_index,
        discount_applied_inr=request.applied_discount_inr,
        selected_size=request.size,
        sku_id=request.sku_id,
        used_fit_check=request.has_used_fit_twin,
        consent_status="opted_in",
        dispatch_priority=dispatch_priority,
        is_synthetic=False,
    )
    session.add(order)

    # Initial delivery event
    initial_event = DeliveryEventModel(
        id=f"evt_{uuid.uuid4().hex[:12]}",
        order_id=order_id,
        event_type="Order_Placed",
        reason=f"Payment: {request.payment_method.upper()}, Total: ₹{total_inr:.2f}",
    )
    session.add(initial_event)

    # Track UPI incentive conversion intervention if applicable
    if (
        request.applied_discount_inr > Decimal("0.00")
        and request.payment_method.upper() == "PREPAID"
    ):
        intervention = IncentiveInterventionModel(
            id=f"int_{uuid.uuid4().hex[:12]}",
            order_id=order_id,
            original_payment="COD",
            offered_discount_inr=request.applied_discount_inr,
            converted_to_upi=True,
            expected_savings_inr=Decimal("52.00"),
            retained_headroom_inr=Decimal("12.00"),
            reason_code=request.incentive_reason_code or "REASON_ELEVATED_RISK_CONVERTIBLE",
        )
        session.add(intervention)

    # Record Fit-Twin audit log if shopper used sizing check
    if request.has_used_fit_twin and request.known_brand and request.known_size:
        rec = recommend_size(
            sku_id=request.sku_id,
            known_brand=request.known_brand,
            known_size=request.known_size,
            fit_preference=request.fit_preference or "tailored",
        )
        fit_log = FitLogModel(
            id=f"fit_{uuid.uuid4().hex[:12]}",
            sku_id=request.sku_id,
            order_id=order_id,
            known_brand=request.known_brand,
            known_size=request.known_size,
            recommended_size=rec.recommended_size,
            confidence_level=rec.confidence_level,
            fit_score=rec.fit_score,
        )
        session.add(fit_log)

    await session.commit()
    await session.refresh(order)
    return _model_to_response(order)


@router.get(
    "",
    response_model=OrderListResponse,
    summary="List customer orders",
    description="Retrieve chronological list of orders for real-time merchant stream.",
    tags=["Orders"],
)
async def list_orders(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> OrderListResponse:
    """List recent orders descending by creation date."""
    repo = OrderRepository(session)
    orders = await repo.list_orders(limit=limit, offset=offset)
    total = await repo.count_orders()
    return OrderListResponse(
        orders=[_model_to_response(o) for o in orders],
        total=total,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get single order details",
    description="Retrieve single order by internal ID or order number.",
    tags=["Orders"],
)
async def get_order(
    order_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> OrderResponse:
    """Retrieve single order by ID or 404."""
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)
    if not order:
        order = await repo.get_by_order_number(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found",
        )
    return _model_to_response(order)


@router.post(
    "/{order_id}/verify",
    response_model=OrderResponse,
    summary="Verify address and confirm delivery slot via WhatsApp simulator",
    description="Updates order with verified landmark, transitions status to 'Safe_For_Dispatch', and logs event.",
    tags=["Orders"],
)
async def verify_order(
    order_id: str,
    request: OrderVerifyRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> OrderResponse:
    """Verify delivery landmark and slot from WhatsApp simulator."""
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)
    if not order:
        order = await repo.get_by_order_number(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found",
        )

    if not request.opt_in_whatsapp:
        order.consent_status = "opted_out"
        event = DeliveryEventModel(
            id=f"evt_{uuid.uuid4().hex[:12]}",
            order_id=order.id,
            event_type="WhatsApp_Opt_Out",
            reason="Customer sent STOP",
        )
        session.add(event)
        await session.commit()
        await session.refresh(order)
        return _model_to_response(order)

    # If landmark provided, run conversational address normalizer
    if request.landmark:
        normalizer = AddressNormalizer()
        norm_result = await normalizer.normalize(
            raw_address=order.street_address,
            landmark=request.landmark,
        )
        if norm_result.landmark:
            order.street_address = f"{norm_result.sanitized_address}, Near {norm_result.landmark}"
        else:
            order.street_address = norm_result.sanitized_address
        order.address_status = "Complete"

    order.order_status = "Safe_For_Dispatch"
    order.consent_status = "opted_in"

    details = []
    if request.landmark:
        details.append(f"Landmark: {request.landmark}")
    if request.delivery_slot:
        details.append(f"Slot: {request.delivery_slot}")
    detail_str = ", ".join(details) if details else "Direct slot confirmation"

    event = DeliveryEventModel(
        id=f"evt_{uuid.uuid4().hex[:12]}",
        order_id=order.id,
        event_type="Address_Verified",
        reason=detail_str,
    )
    session.add(event)
    await session.commit()
    await session.refresh(order)
    return _model_to_response(order)


@router.post(
    "/{order_id}/ndr",
    response_model=OrderResponse,
    summary="Handle Non-Delivery Report (NDR) reschedule",
    description="Reschedules failed delivery attempt and sets status to 'Delivery_Rescheduled'.",
    tags=["Orders"],
)
async def ndr_order(
    order_id: str,
    request: OrderNdrRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> OrderResponse:
    """Reschedule delivery after an NDR event."""
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)
    if not order:
        order = await repo.get_by_order_number(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found",
        )

    order.order_status = "Delivery_Rescheduled"
    event = DeliveryEventModel(
        id=f"evt_{uuid.uuid4().hex[:12]}",
        order_id=order.id,
        event_type="NDR_Rescheduled",
        reason=f"Rescheduled for {request.reschedule_date} ({request.reschedule_slot})",
    )
    session.add(event)
    await session.commit()
    await session.refresh(order)
    return _model_to_response(order)
