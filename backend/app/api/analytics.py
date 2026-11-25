"""Analytics API Endpoints for ReturnZero AI.

Provides live database telemetry overview and interactive 10,000-shipment financial
scenario modeler endpoints per ADR-005, ADR-007, and AGENTS.md §7.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.api_contracts import (
    AnalyticsOverviewResponse,
    ScenarioCalculationRequest,
    ScenarioCalculationResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Live Merchant Telemetry Overview",
    description="Returns live KPI metrics dynamically aggregated from database rows (orders, interventions, returns).",
    tags=["Analytics"],
)
async def get_overview(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnalyticsOverviewResponse:
    """Retrieve live merchant dashboard metrics."""
    service = AnalyticsService(session)
    return await service.get_overview()


@router.get(
    "/scenario",
    response_model=ScenarioCalculationResponse,
    summary="10,000-Shipment Financial Scenario Modeler",
    description="Evaluates closed-form financial projections using pure domain logic. Defaults to deck economics.",
    tags=["Analytics"],
)
async def get_scenario(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    monthly_shipments: Annotated[
        int,
        Query(ge=1, le=1000000, description="Monthly shipment volume"),
    ] = 10000,
    cod_share_pct: Annotated[
        float,
        Query(ge=0.0, le=100.0, description="COD share %"),
    ] = 65.0,
    cod_rto_pct: Annotated[
        float,
        Query(ge=0.0, le=100.0, description="Baseline COD RTO %"),
    ] = 26.0,
    prepaid_rto_pct: Annotated[
        float,
        Query(ge=0.0, le=100.0, description="Prepaid RTO %"),
    ] = 2.0,
    cost_per_rto_inr: Annotated[
        Decimal,
        Query(ge=Decimal("0.00"), description="Cost per RTO in INR"),
    ] = Decimal("200.00"),
    incentive_offer_inr: Annotated[
        Decimal,
        Query(ge=Decimal("0.00"), description="Incentive offer in INR"),
    ] = Decimal("40.00"),
    cod_conversion_pct: Annotated[
        float,
        Query(ge=0.0, le=100.0, description="COD conversion %"),
    ] = 10.0,
    residual_cod_rto_reduction_pp: Annotated[
        float,
        Query(ge=0.0, le=100.0, description="Residual COD RTO improvement pp"),
    ] = 2.0,
    upi_gateway_fee_pct: Annotated[
        float,
        Query(ge=0.0, le=10.0, description="Payment gateway fee %"),
    ] = 0.0,
    average_order_value_inr: Annotated[
        Decimal,
        Query(
            ge=Decimal("100.00"), description="Average order value (INR) for gateway fee projection"
        ),
    ] = Decimal("1899.00"),
) -> ScenarioCalculationResponse:
    """Evaluate financial scenario projections with custom or default parameters."""
    req = ScenarioCalculationRequest(
        monthly_shipments=monthly_shipments,
        cod_share_pct=cod_share_pct,
        cod_rto_pct=cod_rto_pct,
        prepaid_rto_pct=prepaid_rto_pct,
        cost_per_rto_inr=cost_per_rto_inr,
        incentive_offer_inr=incentive_offer_inr,
        cod_conversion_pct=cod_conversion_pct,
        residual_cod_rto_reduction_pp=residual_cod_rto_reduction_pp,
        upi_gateway_fee_pct=upi_gateway_fee_pct,
        average_order_value_inr=average_order_value_inr,
    )
    service = AnalyticsService(session)
    return service.calculate_scenario_projection(req)
