"""Unit tests for explainable operational risk evaluator in app.domain.risk.

Verifies frozen RiskConfig weights, explainable factor attribution, Order Review checks,
and strict preservation of COD availability per ADR-003 and AGENTS.md §5 (E3).
"""

from app.domain.risk import (
    DEFAULT_RISK_CONFIG,
    evaluate_order_risk,
)


class TestRiskConfig:
    """Verifies frozen configuration weights."""

    def test_default_weights_integrity(self) -> None:
        cfg = DEFAULT_RISK_CONFIG
        assert cfg.baseline_risk == 10
        assert cfg.cod_penalty == 25
        assert cfg.high_risk_pin_penalty == 20
        assert cfg.needs_landmark_penalty == 15
        assert cfg.poor_address_penalty == 30
        assert cfg.unverified_fit_penalty == 25
        assert cfg.bracketing_penalty == 40
        assert cfg.fit_verified_bonus == 0
        assert cfg.review_threshold == 40
        assert cfg.elevated_threshold == 70

    def test_risk_config_is_frozen(self) -> None:
        from dataclasses import FrozenInstanceError

        import pytest

        cfg = DEFAULT_RISK_CONFIG
        with pytest.raises(FrozenInstanceError):
            cfg.cod_penalty = 50  # type: ignore[misc]


class TestRiskEvaluation:
    """Tests risk scoring calculations and factors."""

    def test_low_risk_prepaid_order(self) -> None:
        """Prepaid order with complete address and verified fit should be Low risk."""
        result = evaluate_order_risk(
            payment_method="Prepaid",
            street_address="Flat 402, Sai Residency, near Hanuman Mandir",
            pin_code="110001",
            has_used_fit_twin=True,
            is_bracketing=False,
        )
        assert result.risk_score_index == 10
        assert result.risk_level == "Low"
        assert result.cod_remains_available is True
        assert len(result.contributing_factors) == 0

        # Check all 3 checks pass
        checks_by_id = {c.id: c.status for c in result.checks}
        assert checks_by_id["address_quality"] == "PASS"
        assert checks_by_id["serviceable_pin"] == "PASS"
        assert checks_by_id["rto_risk"] == "PASS"

    def test_cod_with_high_risk_pin_yields_review_level(self) -> None:
        """COD (+25) + High-risk PIN 143001 (+20) -> Score 55 (Review)."""
        result = evaluate_order_risk(
            payment_method="COD",
            street_address="Flat 402, Sai Residency, near Hanuman Mandir",
            pin_code="143001",
            has_used_fit_twin=True,
            is_bracketing=False,
        )
        assert result.risk_score_index == 55
        assert result.risk_level == "Review"
        assert any("Cash on Delivery (+25)" in f for f in result.contributing_factors)
        assert any(
            "High-risk synthetic delivery lane PIN 143001 (+20)" in f
            for f in result.contributing_factors
        )

        checks_by_id = {c.id: c.status for c in result.checks}
        assert checks_by_id["rto_risk"] == "REVIEW"

    def test_elevated_risk_with_unverified_fit_and_needs_landmark(self) -> None:
        """COD (+25) + Unverified Fit (+25) + NeedsLandmark (+15) + High-risk PIN (+20) -> 95 (Elevated)."""
        result = evaluate_order_risk(
            payment_method="COD",
            street_address="Flat 301, Hillview, Floor 3",  # Missing landmark
            pin_code="276001",  # Azamgarh (High-risk)
            has_used_fit_twin=False,
            is_bracketing=False,
        )
        assert result.risk_score_index == 95
        assert result.risk_level == "Elevated"
        assert any("Fit-Twin sizing verification (+25)" in f for f in result.contributing_factors)
        assert any("lacks distinct landmark" in f for f in result.contributing_factors)

        checks_by_id = {c.id: c.status for c in result.checks}
        assert checks_by_id["address_quality"] == "REVIEW"
        assert checks_by_id["rto_risk"] == "FAIL"

    def test_bracketing_penalty_application(self) -> None:
        """Bracketing behavior should add +40 penalty points."""
        result = evaluate_order_risk(
            payment_method="Prepaid",
            street_address="Flat 402, Sai Residency, near Hanuman Mandir",
            pin_code="110001",
            has_used_fit_twin=True,
            is_bracketing=True,
        )
        assert result.risk_score_index == 50  # 10 + 40
        assert any(
            "Bracketing flag" in f or "multiple sizes" in f for f in result.contributing_factors
        )

    def test_unserviceable_pin_marks_check_fail(self) -> None:
        """Unserviceable PIN should fail the serviceable_pin check."""
        result = evaluate_order_risk(
            payment_method="Prepaid",
            street_address="Flat 402, Sai Residency, near Hanuman Mandir",
            pin_code="999999",
        )
        checks_by_id = {c.id: c.status for c in result.checks}
        assert checks_by_id["serviceable_pin"] == "FAIL"

    def test_score_never_exceeds_100(self) -> None:
        """Max penalty combinations must cap cleanly at 100."""
        result = evaluate_order_risk(
            payment_method="COD",  # +25
            street_address="Short",  # Poor address +30
            pin_code="143001",  # High-risk +20
            has_used_fit_twin=False,  # +25
            is_bracketing=True,  # +40
        )
        # Total would be 10 + 25 + 30 + 20 + 25 + 40 = 150 -> Capped at 100
        assert result.risk_score_index == 100
        assert result.risk_level == "Elevated"
        assert result.cod_remains_available is True
