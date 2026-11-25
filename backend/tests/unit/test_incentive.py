"""Unit tests for closed-form margin-safe incentive solver in app.domain.incentive.

Verifies exact pitch deck calculations, 1.5% fee policy margin protection,
coupon stacking cap (<=20% GMV), and doorstep refusal guardrails per ADR-002 and ADR-014.
"""

from decimal import Decimal

from app.domain.incentive import (
    REASON_COUPON_CAP,
    REASON_ELEVATED_RISK_CONVERTIBLE,
    REASON_INSUFFICIENT_MARGIN,
    REASON_LOW_RISK,
    REASON_PREPAID_OPTIMAL,
    REASON_REPEAT_REFUSAL,
    calculate_incentive_quote,
)


class TestIncentiveSolverBaseline:
    """Tests the pitch deck baseline calculation and eligibility."""

    def test_default_1899_cart_yields_40_rupee_offer_and_8_headroom(self) -> None:
        """Pitch deck canonical: ₹1,899 cart, 0% fee -> ₹40 offer, ₹8 headroom, eligible."""
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("1899.00"),
            risk_score_index=45,
            current_payment="COD",
            has_used_fit_twin=True,
            upi_gateway_fee_pct=Decimal("0.0"),
        )
        assert result.eligible_for_incentive is True
        assert result.recommended_discount_inr == Decimal("40.00")
        assert result.expected_avoided_loss_inr == Decimal("48.00")
        assert result.expected_savings_inr == Decimal("8.00")
        assert result.headroom_inr == Decimal("8.00")
        assert result.reason_code == REASON_ELEVATED_RISK_CONVERTIBLE
        assert result.cod_remains_available is True
        assert "₹40.00" in result.nudge_copy or "₹40" in result.nudge_copy

    def test_prepaid_order_is_optimal_and_ineligible(self) -> None:
        """Prepaid orders already have secured margin; no discount offered."""
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("1899.00"),
            risk_score_index=45,
            current_payment="Prepaid",
        )
        assert result.eligible_for_incentive is False
        assert result.recommended_discount_inr == Decimal("0.00")
        assert result.reason_code == REASON_PREPAID_OPTIMAL

    def test_low_risk_cod_order_is_ineligible(self) -> None:
        """Low risk COD order (risk score < 40) proceeds with standard checkout."""
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("1899.00"),
            risk_score_index=25,
            current_payment="COD",
        )
        assert result.eligible_for_incentive is False
        assert result.recommended_discount_inr == Decimal("0.00")
        assert result.reason_code == REASON_LOW_RISK


class TestConfigurableFeePolicy:
    """Verifies margin defense when non-zero gateway fees are simulated (ADR-002)."""

    def test_gateway_fee_1_5_percent_makes_1899_cart_ineligible(self) -> None:
        """With 1.5% fee on ₹1,899, D_max = 48 - 28.49 - 8 = ₹11.51 < ₹25 (Ineligible).

        Demonstrates margin protection: dynamically withdraws offer instead of eroding margin.
        """
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("1899.00"),
            risk_score_index=45,
            current_payment="COD",
            upi_gateway_fee_pct=Decimal("0.015"),
        )
        assert result.eligible_for_incentive is False
        assert result.recommended_discount_inr == Decimal("0.00")
        assert result.expected_avoided_loss_inr == Decimal("0.00")
        assert result.reason_code == REASON_INSUFFICIENT_MARGIN


class TestAntiAbuseControls:
    """Verifies coupon stacking cap and repeat doorstep refusal rules (ADR-014)."""

    def test_coupon_stacking_cap_at_20_percent_gmv(self) -> None:
        """On ₹1,899 cart, max allowable discount is 20% = ₹379.80.

        If merchant coupon of ₹360 is applied, remaining headroom is ₹19.80 < ₹25 min offer.
        Solver must withhold cash discount with REASON_COUPON_CAP.
        """
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("1899.00"),
            risk_score_index=45,
            current_payment="COD",
            applied_coupon_discount_inr=Decimal("360.00"),
        )
        assert result.eligible_for_incentive is False
        assert result.recommended_discount_inr == Decimal("0.00")
        assert result.reason_code == REASON_COUPON_CAP
        assert "promotional coupon" in result.nudge_copy

    def test_coupon_headroom_caps_discount_to_remaining_margin(self) -> None:
        """When remaining GMV headroom is between ₹25 and ₹40, discount is capped by headroom."""
        # On ₹2,000 cart, 20% cap = ₹400. Coupon = ₹370 -> Remaining headroom = ₹30.
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("2000.00"),
            risk_score_index=50,
            current_payment="COD",
            applied_coupon_discount_inr=Decimal("370.00"),
        )
        assert result.eligible_for_incentive is True
        assert result.recommended_discount_inr == Decimal("30.00")

    def test_unverified_fit_twin_nudge_copy(self) -> None:
        """When fit is not verified, customer nudge uses generic UPI switch copy."""
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("1899.00"),
            risk_score_index=45,
            current_payment="COD",
            has_used_fit_twin=False,
        )
        assert result.eligible_for_incentive is True
        assert "Switch to instant UPI now to save" in result.nudge_copy

    def test_repeat_refusal_withholds_cash_offers_care_kit(self) -> None:
        """3 consecutive doorstep refusals must withhold cash discount in favor of non-cash perk."""
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("1899.00"),
            risk_score_index=45,
            current_payment="COD",
            doorstep_refusal_count=3,
        )
        assert result.eligible_for_incentive is False
        assert result.recommended_discount_inr == Decimal("0.00")
        assert result.reason_code == REASON_REPEAT_REFUSAL
        assert "garment care kit" in result.nudge_copy


class TestOfferDiscretization:
    """Verifies that discount rounding strictly floors to ₹5 step and never rounds up."""

    def test_discount_rounding_floors_to_step(self) -> None:
        # If D_max would be 34.00, floor to 5 step yields 30.00 (not 35.00)
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("1000.00"),
            risk_score_index=50,
            current_payment="COD",
            direct_cost_per_rto=Decimal(
                "170.00"
            ),  # Avoided = 0.24 * 170 = 40.80. D_max = 40.80 - 8 = 32.80
        )
        assert result.eligible_for_incentive is True
        assert result.recommended_discount_inr == Decimal("30.00")
        assert result.recommended_discount_inr <= Decimal("32.80")

    def test_floored_discount_under_custom_min_offer_ineligible(self) -> None:
        # When max_allowable_discount is 28.00 and custom min_offer is 26.00,
        # floored_discount becomes 25.00 < 26.00, triggering branch line 170
        result = calculate_incentive_quote(
            cart_total_inr=Decimal("1000.00"),
            risk_score_index=50,
            current_payment="COD",
            direct_cost_per_rto=Decimal(
                "150.00"
            ),  # Avoided = 0.24 * 150 = 36.00. D_max = 36 - 8 = 28.00
            min_offer=Decimal("26.00"),
        )
        assert result.eligible_for_incentive is False
        assert result.recommended_discount_inr == Decimal("0.00")
        assert result.expected_avoided_loss_inr == Decimal("0.00")
        assert result.reason_code == REASON_INSUFFICIENT_MARGIN
