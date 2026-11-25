"""Unit tests for pure financial scenario modeler in app.domain.scenario.

Verifies exact mathematical parity with ReturnZero pitch deck economics (Slide 5,
SOURCES_AND_ASSUMPTIONS.md, and ADR-005) with zero error.
"""

from decimal import Decimal

from app.domain.scenario import (
    SAVINGS_DISCLAIMER,
    calculate_scenario,
)


class TestFinancialScenarioParity:
    """Verifies that calculate_scenario reproduces deck figures with 0.00 error."""

    def test_baseline_figures_match_pitch_deck(self) -> None:
        scenario = calculate_scenario()
        assert scenario.monthly_shipments == 10_000
        assert scenario.baseline_cod_shipments == 6_500
        assert scenario.baseline_prepaid_shipments == 3_500
        assert scenario.baseline_cod_rto == 1_690
        assert scenario.baseline_prepaid_rto == 70
        assert scenario.baseline_total_rto == 1_760
        assert scenario.baseline_cost_inr == Decimal("352000.00")

    def test_combined_scenario_matches_deck_exactly(self) -> None:
        """Combined: 10% COD converted + 2pp residual COD improvement."""
        scenario = calculate_scenario()
        comb = scenario.combined_scenario

        assert comb.converted_shipments == 650
        assert comb.remaining_cod_shipments == 5_850
        assert comb.prepaid_shipments == 4_150
        assert comb.cod_rto_shipments == 1_404
        assert comb.prepaid_rto_shipments == 83
        assert comb.total_rto_shipments == 1_487
        assert comb.avoided_rto_shipments == 273
        assert comb.gross_avoided_cost_inr == Decimal("54600.00")
        assert comb.incentives_paid_inr == Decimal("26000.00")
        assert comb.monthly_direct_net_savings_inr == Decimal("28600.00")
        assert comb.annual_direct_net_savings_inr == Decimal("343200.00")

    def test_conservative_scenario_matches_deck_exactly(self) -> None:
        """Conservative: Conversion-only (10% COD shifted), 0pp residual improvement."""
        scenario = calculate_scenario()
        cons = scenario.conservative_scenario

        assert cons.converted_shipments == 650
        assert cons.remaining_cod_shipments == 5_850
        assert cons.prepaid_shipments == 4_150
        assert cons.cod_rto_shipments == 1_521
        assert cons.prepaid_rto_shipments == 83
        assert cons.total_rto_shipments == 1_604
        assert cons.avoided_rto_shipments == 156
        assert cons.gross_avoided_cost_inr == Decimal("31200.00")
        assert cons.incentives_paid_inr == Decimal("26000.00")
        assert cons.monthly_direct_net_savings_inr == Decimal("5200.00")
        assert cons.annual_direct_net_savings_inr == Decimal("62400.00")

    def test_disclaimers_integrity(self) -> None:
        scenario = calculate_scenario()
        assert "modelled direct operating savings" in scenario.disclaimer
        assert scenario.disclaimer == SAVINGS_DISCLAIMER

    def test_scenario_deducts_gateway_fees_when_nonzero(self) -> None:
        """Gateway fee > 0% deducts fees per converted UPI order from net savings."""
        scenario = calculate_scenario(
            upi_gateway_fee_pct=Decimal("0.015"),
            average_order_value_inr=Decimal("1899.00"),
        )
        comb = scenario.combined_scenario
        # 650 converted orders * round(1899 * 0.015 = 28.49) = 18518.50
        assert comb.payment_fees_inr == Decimal("18518.50")
        assert comb.monthly_direct_net_savings_inr == (
            comb.gross_avoided_cost_inr - comb.incentives_paid_inr - comb.payment_fees_inr
        )
        assert comb.monthly_direct_net_savings_inr == Decimal("10081.50")
