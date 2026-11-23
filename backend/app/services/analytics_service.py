"""Analytics Service for ReturnZero AI.

Coordinates live synthetic database telemetry aggregation and interactive
10,000-shipment financial scenario modeling. Strictly maintains physical and
logical segregation between live DB telemetry and scenario models per ADR-005.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import AnalyticsRepository
from app.domain.scenario import (
    SAVINGS_DISCLAIMER,
    ScenarioProjection,
    ScenarioResult,
    calculate_scenario,
)
from app.schemas.api_contracts import (
    AnalyticsOverviewResponse,
    ScenarioCalculationRequest,
    ScenarioCalculationResponse,
    ScenarioOutputsSchema,
)


class AnalyticsService:
    """Service providing live merchant telemetry and financial scenario modeling."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AnalyticsRepository(session)

    async def get_overview(self) -> AnalyticsOverviewResponse:
        """Fetch dynamic analytics aggregated directly from database tables."""
        return await self.repo.get_live_overview()

    @staticmethod
    def _map_projection(res: ScenarioResult, proj: ScenarioProjection) -> ScenarioOutputsSchema:
        """Map a domain ScenarioProjection to API ScenarioOutputsSchema."""
        baseline_rate = (
            round((res.baseline_total_rto / res.monthly_shipments * 100.0), 2)
            if res.monthly_shipments > 0
            else 0.0
        )
        new_rate = (
            round((proj.total_rto_shipments / res.monthly_shipments * 100.0), 2)
            if res.monthly_shipments > 0
            else 0.0
        )

        return ScenarioOutputsSchema(
            baseline_cod_shipments=res.baseline_cod_shipments,
            baseline_prepaid_shipments=res.baseline_prepaid_shipments,
            baseline_cod_rto_shipments=res.baseline_cod_rto,
            baseline_prepaid_rto_shipments=res.baseline_prepaid_rto,
            baseline_total_rto_shipments=res.baseline_total_rto,
            baseline_rto_rate_pct=baseline_rate,
            converted_shipments=proj.converted_shipments,
            new_cod_shipments=proj.remaining_cod_shipments,
            new_prepaid_shipments=proj.prepaid_shipments,
            new_cod_rto_shipments=proj.cod_rto_shipments,
            new_prepaid_rto_shipments=proj.prepaid_rto_shipments,
            new_total_rto_shipments=proj.total_rto_shipments,
            new_rto_rate_pct=new_rate,
            avoided_rto_shipments=proj.avoided_rto_shipments,
            gross_avoided_loss_inr=proj.gross_avoided_cost_inr,
            total_incentives_paid_inr=proj.incentives_paid_inr,
            total_payment_fees_inr=Decimal("0.00"),
            net_operating_savings_monthly_inr=proj.monthly_direct_net_savings_inr,
            net_operating_savings_annual_inr=proj.annual_direct_net_savings_inr,
        )

    def calculate_scenario_projection(
        self,
        request: ScenarioCalculationRequest,
    ) -> ScenarioCalculationResponse:
        """Execute pure domain scenario calculation reproducing pitch deck economics."""
        # Convert request percentages from 0-100 to 0-1 Decimal for domain solver
        cod_share_dec = Decimal(str(request.cod_share_pct)) / Decimal("100")
        cod_rto_dec = Decimal(str(request.cod_rto_pct)) / Decimal("100")
        prepaid_rto_dec = Decimal(str(request.prepaid_rto_pct)) / Decimal("100")
        conversion_dec = Decimal(str(request.cod_conversion_pct)) / Decimal("100")
        residual_dec = Decimal(str(request.residual_cod_rto_reduction_pp)) / Decimal("100")

        result: ScenarioResult = calculate_scenario(
            monthly_shipments=request.monthly_shipments,
            cod_share_pct=cod_share_dec,
            cod_rto_rate_pct=cod_rto_dec,
            prepaid_rto_rate_pct=prepaid_rto_dec,
            direct_cost_per_rto=request.cost_per_rto_inr,
            cod_to_prepaid_shift_pct=conversion_dec,
            incentive_per_order=request.incentive_offer_inr,
            residual_cod_rto_improvement_pp=residual_dec,
        )

        return ScenarioCalculationResponse(
            combined_case=self._map_projection(result, result.combined_scenario),
            conservative_conversion_only_case=self._map_projection(
                result, result.conservative_scenario
            ),
            disclaimer=SAVINGS_DISCLAIMER,
        )
