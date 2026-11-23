"""Pure 10,000-shipment financial scenario modeler for ReturnZero AI.

Mathematically reproduces pitch deck unit economics with zero error.
Strictly segregates scenario modeling from live database telemetry per ADR-005.
Savings are explicitly defined as:
'modelled direct operating savings after incentives, before fees'.
Reference: ADR-005, AGENTS.md §5 (E5), §6.2 & §9.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final

from app.domain.money import (
    quantize_currency,
    to_decimal,
)

# Standard pitch deck baseline inputs (ADR-005, FINAL_DECK_COPY.md Slide 5)
DEFAULT_MONTHLY_SHIPMENTS: Final[int] = 10_000
DEFAULT_COD_SHARE: Final[Decimal] = Decimal("0.65")  # 65% COD mix
DEFAULT_COD_RTO_RATE: Final[Decimal] = Decimal("0.26")  # 26% Shipway FY25 benchmark
DEFAULT_PREPAID_RTO_RATE: Final[Decimal] = Decimal("0.02")  # 2% prepaid benchmark
DEFAULT_COST_PER_RTO: Final[Decimal] = Decimal(
    "200.00"
)  # Illustrative direct carrier & handling cost
DEFAULT_COD_CONVERSION_RATE: Final[Decimal] = Decimal("0.10")  # 10% of COD shifted to prepaid
DEFAULT_INCENTIVE_PER_ORDER: Final[Decimal] = Decimal("40.00")  # ₹40 incentive per converted order
DEFAULT_RESIDUAL_COD_IMPROVEMENT_PP: Final[Decimal] = Decimal(
    "0.02"
)  # 2 pp improvement from delivery assurance

SAVINGS_DISCLAIMER: Final[str] = (
    "modelled direct operating savings after incentives, before fees — "
    "excluding tax, overhead, and other non-delivery costs."
)
RTO_COST_NOTE: Final[str] = (
    "For illustration, the model assumes ₹200 in direct cost per failed delivery. "
    "That is a scenario input, not an India-wide average; replace it with actual carrier and handling costs."
)


@dataclass(frozen=True)
class ScenarioProjection:
    """Projections for a specific intervention scenario (Combined or Conservative)."""

    converted_shipments: int
    remaining_cod_shipments: int
    prepaid_shipments: int
    cod_rto_shipments: int
    prepaid_rto_shipments: int
    total_rto_shipments: int
    avoided_rto_shipments: int
    gross_avoided_cost_inr: Decimal
    incentives_paid_inr: Decimal
    monthly_direct_net_savings_inr: Decimal
    annual_direct_net_savings_inr: Decimal
    label: str


@dataclass(frozen=True)
class ScenarioResult:
    """Complete 10,000-shipment financial scenario evaluation."""

    monthly_shipments: int
    baseline_cod_shipments: int
    baseline_prepaid_shipments: int
    baseline_cod_rto: int
    baseline_prepaid_rto: int
    baseline_total_rto: int
    baseline_cost_inr: Decimal
    combined_scenario: ScenarioProjection
    conservative_scenario: ScenarioProjection
    disclaimer: str = SAVINGS_DISCLAIMER
    cost_note: str = RTO_COST_NOTE


def calculate_scenario(
    monthly_shipments: int = DEFAULT_MONTHLY_SHIPMENTS,
    cod_share_pct: Decimal | int | str = DEFAULT_COD_SHARE,
    cod_rto_rate_pct: Decimal | int | str = DEFAULT_COD_RTO_RATE,
    prepaid_rto_rate_pct: Decimal | int | str = DEFAULT_PREPAID_RTO_RATE,
    direct_cost_per_rto: Decimal | int | str = DEFAULT_COST_PER_RTO,
    cod_to_prepaid_shift_pct: Decimal | int | str = DEFAULT_COD_CONVERSION_RATE,
    incentive_per_order: Decimal | int | str = DEFAULT_INCENTIVE_PER_ORDER,
    residual_cod_rto_improvement_pp: Decimal | int | str = DEFAULT_RESIDUAL_COD_IMPROVEMENT_PP,
) -> ScenarioResult:
    """Calculate 10,000-shipment financial projection with pitch deck parity.

    Pure domain function with zero side-effects. Follows ADR-005 and AGENTS.md §6.2.
    """
    cod_share = to_decimal(cod_share_pct)
    cod_rto_rate = to_decimal(cod_rto_rate_pct)
    prepaid_rto_rate = to_decimal(prepaid_rto_rate_pct)
    cost_per_rto = to_decimal(direct_cost_per_rto)
    shift_pct = to_decimal(cod_to_prepaid_shift_pct)
    incentive_amt = to_decimal(incentive_per_order)
    residual_pp = to_decimal(residual_cod_rto_improvement_pp)

    # 1. Baseline Calculations
    base_cod_shipments = int(Decimal(str(monthly_shipments)) * cod_share)
    base_prepaid_shipments = monthly_shipments - base_cod_shipments

    base_cod_rto = int(Decimal(str(base_cod_shipments)) * cod_rto_rate)
    base_prepaid_rto = int(Decimal(str(base_prepaid_shipments)) * prepaid_rto_rate)
    base_total_rto = base_cod_rto + base_prepaid_rto
    base_cost = quantize_currency(Decimal(str(base_total_rto)) * cost_per_rto)

    # 2. Converted Cohorts
    converted_shipments = int(Decimal(str(base_cod_shipments)) * shift_pct)
    remaining_cod_shipments = base_cod_shipments - converted_shipments
    new_prepaid_shipments = base_prepaid_shipments + converted_shipments

    # 3. Combined Scenario (Conversion + 2pp residual COD RTO improvement from delivery assurance)
    combined_cod_rate = max(Decimal("0.00"), cod_rto_rate - residual_pp)
    combined_cod_rto = int(Decimal(str(remaining_cod_shipments)) * combined_cod_rate)
    combined_prepaid_rto = int(Decimal(str(new_prepaid_shipments)) * prepaid_rto_rate)
    combined_total_rto = combined_cod_rto + combined_prepaid_rto
    combined_avoided = base_total_rto - combined_total_rto

    combined_gross = quantize_currency(Decimal(str(combined_avoided)) * cost_per_rto)
    combined_incentives = quantize_currency(Decimal(str(converted_shipments)) * incentive_amt)
    combined_monthly_net = combined_gross - combined_incentives
    combined_annual_net = quantize_currency(combined_monthly_net * Decimal("12"))

    combined_proj = ScenarioProjection(
        converted_shipments=converted_shipments,
        remaining_cod_shipments=remaining_cod_shipments,
        prepaid_shipments=new_prepaid_shipments,
        cod_rto_shipments=combined_cod_rto,
        prepaid_rto_shipments=combined_prepaid_rto,
        total_rto_shipments=combined_total_rto,
        avoided_rto_shipments=combined_avoided,
        gross_avoided_cost_inr=combined_gross,
        incentives_paid_inr=combined_incentives,
        monthly_direct_net_savings_inr=combined_monthly_net,
        annual_direct_net_savings_inr=combined_annual_net,
        label="Combined Scenario (COD-to-Prepaid Conversion + Delivery Assurance)",
    )

    # 4. Conservative Scenario (Conversion-only, residual COD RTO remains baseline 26%)
    conservative_cod_rto = int(Decimal(str(remaining_cod_shipments)) * cod_rto_rate)
    conservative_prepaid_rto = int(Decimal(str(new_prepaid_shipments)) * prepaid_rto_rate)
    conservative_total_rto = conservative_cod_rto + conservative_prepaid_rto
    conservative_avoided = base_total_rto - conservative_total_rto

    conservative_gross = quantize_currency(Decimal(str(conservative_avoided)) * cost_per_rto)
    conservative_incentives = quantize_currency(Decimal(str(converted_shipments)) * incentive_amt)
    conservative_monthly_net = conservative_gross - conservative_incentives
    conservative_annual_net = quantize_currency(conservative_monthly_net * Decimal("12"))

    conservative_proj = ScenarioProjection(
        converted_shipments=converted_shipments,
        remaining_cod_shipments=remaining_cod_shipments,
        prepaid_shipments=new_prepaid_shipments,
        cod_rto_shipments=conservative_cod_rto,
        prepaid_rto_shipments=conservative_prepaid_rto,
        total_rto_shipments=conservative_total_rto,
        avoided_rto_shipments=conservative_avoided,
        gross_avoided_cost_inr=conservative_gross,
        incentives_paid_inr=conservative_incentives,
        monthly_direct_net_savings_inr=conservative_monthly_net,
        annual_direct_net_savings_inr=conservative_annual_net,
        label="Conservative Scenario (Conversion-Only, No Residual COD Improvement)",
    )

    return ScenarioResult(
        monthly_shipments=monthly_shipments,
        baseline_cod_shipments=base_cod_shipments,
        baseline_prepaid_shipments=base_prepaid_shipments,
        baseline_cod_rto=base_cod_rto,
        baseline_prepaid_rto=base_prepaid_rto,
        baseline_total_rto=base_total_rto,
        baseline_cost_inr=base_cost,
        combined_scenario=combined_proj,
        conservative_scenario=conservative_proj,
    )
