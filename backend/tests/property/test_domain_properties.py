"""Property-based invariant and boundary testing for ReturnZero pure domain modules.

Verifies mathematical invariants, monotonicity, bounds, and consistency across
synthetic parameter sweeps per AGENTS.md §6.4 and IMPLEMENTATION_PLAN.md §3.
"""

import random
from decimal import Decimal

from app.domain.address import address_quality
from app.domain.incentive import calculate_incentive_quote
from app.domain.risk import evaluate_order_risk
from app.domain.scenario import calculate_scenario
from app.domain.sizing import recommend_size


class TestIncentiveInvariants:
    """Verifies invariant properties of the dynamic incentive solver."""

    def test_discount_bounds_and_discretization_sweep(self) -> None:
        """Discount must always be 0.00 OR between 25.00 and 40.00 in steps of 5.00."""
        rng = random.Random(42)
        valid_discount_steps = {
            Decimal("0.00"),
            Decimal("25.00"),
            Decimal("30.00"),
            Decimal("35.00"),
            Decimal("40.00"),
        }

        for _ in range(200):
            cart = Decimal(str(rng.randint(500, 10000)))
            risk = rng.randint(0, 100)
            pm = rng.choice(["COD", "Prepaid"])
            coupon = Decimal(str(rng.randint(0, 500)))
            refusals = rng.randint(0, 5)
            fee = Decimal(str(rng.choice(["0.0", "0.01", "0.015", "0.02"])))

            quote = calculate_incentive_quote(
                cart_total_inr=cart,
                risk_score_index=risk,
                current_payment=pm,
                applied_coupon_discount_inr=coupon,
                doorstep_refusal_count=refusals,
                upi_gateway_fee_pct=fee,
            )

            # Invariant 1: discount is discrete
            assert quote.recommended_discount_inr in valid_discount_steps

            # Invariant 2: total discount (coupon + quote) never exceeds 20% of GMV
            total_discount = coupon + quote.recommended_discount_inr
            assert total_discount <= (
                cart * Decimal("0.20")
            ) or quote.recommended_discount_inr == Decimal("0.00")

            # Invariant 3: COD remains available is unconditionally True
            assert quote.cod_remains_available is True

            # Invariant 4: If ineligible, discount is exactly zero
            if not quote.eligible_for_incentive:
                assert quote.recommended_discount_inr == Decimal("0.00")
            else:
                assert quote.recommended_discount_inr >= Decimal("25.00")


class TestRiskInvariants:
    """Verifies invariant properties of the operational risk evaluator."""

    def test_risk_score_always_bounded_between_0_and_100(self) -> None:
        rng = random.Random(123)
        pins = ["110001", "143001", "276001", "999999", "12345"]
        addresses = [
            "Flat 402, Sai Residency, near Hanuman Mandir",
            "Near temple, station road",
            "House 12",
            "Short",
            "Plot 14, Gandhi Chowk, purani gali",
        ]

        for _ in range(200):
            pm = rng.choice(["COD", "Prepaid", "CARD", "UPI"])
            pin = rng.choice(pins)
            addr = rng.choice(addresses)
            fit = rng.choice([True, False])
            brack = rng.choice([True, False])

            res = evaluate_order_risk(
                payment_method=pm,
                street_address=addr,
                pin_code=pin,
                has_used_fit_twin=fit,
                is_bracketing=brack,
            )

            # Invariant: Score in [0, 100]
            assert 0 <= res.risk_score_index <= 100
            # Invariant: Risk level matches score bands
            if res.risk_score_index < 40:
                assert res.risk_level == "Low"
            elif res.risk_score_index < 70:
                assert res.risk_level == "Review"
            else:
                assert res.risk_level == "Elevated"
            # Invariant: Checks structure
            assert len(res.checks) == 3
            assert res.cod_remains_available is True


class TestSizingInvariants:
    """Verifies monotonicity and confidence bands for sizing engine."""

    def test_sizing_monotonicity(self) -> None:
        """As chest circumference increases, recommended size label never decreases."""
        size_order = ["XS", "S", "M", "L", "XL"]
        sku_ids = ["SKU-01", "SKU-02", "SKU-03", "SKU-04"]

        for sku_id in sku_ids:
            for pref in ["tight", "tailored", "relaxed"]:
                last_idx = 0
                for brand_size in ["S", "M", "L"]:
                    rec = recommend_size(
                        sku_id=sku_id,
                        known_brand="Zara",
                        known_size=brand_size,
                        fit_preference=pref,
                    )
                    curr_idx = size_order.index(rec.recommended_size)
                    assert curr_idx >= last_idx, (
                        f"Monotonicity violation on {sku_id} {pref}: "
                        f"{brand_size} yielded size index {curr_idx} < {last_idx}"
                    )
                    last_idx = curr_idx

    def test_confidence_level_domain_set(self) -> None:
        """Confidence level must strictly be one of High, Medium, Low (Insufficient Data)."""
        valid_confidences = {"High", "Medium", "Low (Insufficient Data)"}
        for sku_id in ["SKU-01", "SKU-02", "SKU-03", "SKU-04", "SKU-UNKNOWN"]:
            for brand in ["Zara", "H&M", "UnknownBrand"]:
                rec = recommend_size(
                    sku_id=sku_id,
                    known_brand=brand,
                    known_size="M",
                )
                assert rec.confidence_level in valid_confidences


class TestAddressInvariants:
    """Verifies domain classifications of address evaluator."""

    def test_address_status_domain_set(self) -> None:
        valid_statuses = {"Complete", "NeedsLandmark", "Poor"}
        test_cases = [
            ("", ""),
            ("12345", "110001"),
            ("Flat 101, Near Mandir", "110001"),
            ("Flat 101, Near Mandir", "invalid"),
        ]
        for addr, pin in test_cases:
            res = address_quality(addr, pin)
            assert res.status in valid_statuses


class TestScenarioInvariants:
    """Verifies mathematical consistency of scenario projections across parameter sweeps."""

    def test_scenario_conservation_laws(self) -> None:
        rng = random.Random(999)
        for _ in range(50):
            shipments = rng.randint(5000, 50000)
            cod_share = Decimal(str(rng.randint(40, 80))) / Decimal("100")
            cod_rto = Decimal(str(rng.randint(15, 35))) / Decimal("100")
            prepaid_rto = Decimal(str(rng.randint(1, 5))) / Decimal("100")

            scen = calculate_scenario(
                monthly_shipments=shipments,
                cod_share_pct=cod_share,
                cod_rto_rate_pct=cod_rto,
                prepaid_rto_rate_pct=prepaid_rto,
            )

            # Invariant 1: Shipments sum conserved
            assert scen.baseline_cod_shipments + scen.baseline_prepaid_shipments == shipments
            # Invariant 2: Total RTO is sum of components
            assert scen.baseline_total_rto == scen.baseline_cod_rto + scen.baseline_prepaid_rto
            # Invariant 3: Avoided RTO = baseline RTO - combined RTO
            assert (
                scen.combined_scenario.avoided_rto_shipments
                == scen.baseline_total_rto - scen.combined_scenario.total_rto_shipments
            )
            # Invariant 4: Annual savings = 12 * monthly savings
            assert (
                scen.combined_scenario.annual_direct_net_savings_inr
                == scen.combined_scenario.monthly_direct_net_savings_inr * Decimal("12")
            )
