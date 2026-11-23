"""Explainable operational risk evaluator for ReturnZero AI.

Evaluates an order risk index (0-100) using transparent, frozen operational rules
covering payment mode, sizing verification, bracketing behavior, address quality,
and synthetic delivery lane history.
Reference: ADR-003, AGENTS.md §5 (E3) & §6.2.
"""

from dataclasses import dataclass, field
from typing import Final, Literal

from app.data.serviceable_pins import ALL_SERVICEABLE_PINS, SYNTHETIC_HIGH_RISK_PINS
from app.domain.address import address_quality

RiskLevel = Literal["Low", "Review", "Elevated"]
CheckStatus = Literal["PASS", "REVIEW", "FAIL"]


@dataclass(frozen=True)
class RiskConfig:
    """Frozen operational weights and classification thresholds for risk scoring."""

    baseline_risk: int = 10
    cod_penalty: int = 25
    high_risk_pin_penalty: int = 20
    needs_landmark_penalty: int = 15
    poor_address_penalty: int = 30
    unverified_fit_penalty: int = 25
    bracketing_penalty: int = 40
    fit_verified_bonus: int = 0  # Non-punitive: adds 0 penalty (ADR-003)
    review_threshold: int = 40
    elevated_threshold: int = 70


DEFAULT_RISK_CONFIG: Final[RiskConfig] = RiskConfig()


@dataclass(frozen=True)
class OrderReviewCheck:
    id: str
    label: str
    status: CheckStatus


@dataclass(frozen=True)
class RiskEvaluationResult:
    risk_score_index: int
    risk_level: RiskLevel
    contributing_factors: list[str] = field(default_factory=list)
    checks: list[OrderReviewCheck] = field(default_factory=list)
    cod_remains_available: bool = True  # Fairness mandate: COD never hard-blocked (ADR-003)


def evaluate_order_risk(
    payment_method: str,
    street_address: str,
    pin_code: str,
    has_used_fit_twin: bool = True,
    is_bracketing: bool = False,
    config: RiskConfig = DEFAULT_RISK_CONFIG,
    custom_high_risk_pins: frozenset[str] | None = None,
    custom_serviceable_pins: frozenset[str] | None = None,
) -> RiskEvaluationResult:
    """Evaluate order risk index and 3-point Order Review checklist.

    Pure domain function with zero side effects. Follows ADR-003 and AGENTS.md §6.2.
    """
    clean_pin = pin_code.strip()
    high_risk_pins = (
        custom_high_risk_pins if custom_high_risk_pins is not None else SYNTHETIC_HIGH_RISK_PINS
    )
    serviceable_pins = (
        custom_serviceable_pins if custom_serviceable_pins is not None else ALL_SERVICEABLE_PINS
    )

    score = config.baseline_risk
    factors: list[str] = []

    # 1. Payment Method Feature
    norm_payment = payment_method.strip().upper()
    if norm_payment == "COD":
        score += config.cod_penalty
        factors.append(f"Payment method: Cash on Delivery (+{config.cod_penalty})")

    # 2. Sizing Verification Signal (ADR-003)
    if not has_used_fit_twin:
        score += config.unverified_fit_penalty
        factors.append(
            f"Shopper bypassed Fit-Twin sizing verification (+{config.unverified_fit_penalty})"
        )

    # 3. Cart Bracketing Behavior (Ordering multiple sizes)
    if is_bracketing:
        score += config.bracketing_penalty
        factors.append(
            f"Cart contains multiple sizes of identical SKU (+{config.bracketing_penalty})"
        )

    # 4. Address Quality Evaluation
    addr_eval = address_quality(street_address, clean_pin)
    if addr_eval.status == "NeedsLandmark":
        score += config.needs_landmark_penalty
        factors.append(
            f"Street address lacks distinct landmark or directional locator (+{config.needs_landmark_penalty})"
        )
    elif addr_eval.status == "Poor":
        score += config.poor_address_penalty
        factors.append(
            f"Street address incomplete or missing premise number (+{config.poor_address_penalty})"
        )

    # 5. Geographic Lane Risk (Synthetic demo lanes per ADR-003)
    if clean_pin in high_risk_pins:
        score += config.high_risk_pin_penalty
        factors.append(
            f"High-risk synthetic delivery lane PIN {clean_pin} (+{config.high_risk_pin_penalty})"
        )

    # Bound score strictly to [0, 100]
    final_score = max(0, min(100, score))

    # Categorize Risk Level
    if final_score < config.review_threshold:
        level: RiskLevel = "Low"
    elif final_score < config.elevated_threshold:
        level = "Review"
    else:
        level = "Elevated"

    # Generate 3-Point Order Review Checklist (ADR-003)
    # Check 1: Address Complete
    if addr_eval.status == "Complete":
        address_status: CheckStatus = "PASS"
    elif addr_eval.status == "NeedsLandmark":
        address_status = "REVIEW"
    else:
        address_status = "FAIL"

    # Check 2: Serviceable PIN
    is_serviceable = clean_pin in serviceable_pins
    pin_status: CheckStatus = "PASS" if is_serviceable else "FAIL"

    # Check 3: RTO Risk Band
    if level == "Low":
        rto_status: CheckStatus = "PASS"
    elif level == "Review":
        rto_status = "REVIEW"
    else:
        rto_status = "FAIL"

    checks = [
        OrderReviewCheck(id="address_quality", label="Address complete", status=address_status),
        OrderReviewCheck(id="serviceable_pin", label="Serviceable PIN", status=pin_status),
        OrderReviewCheck(id="rto_risk", label="RTO risk band", status=rto_status),
    ]

    return RiskEvaluationResult(
        risk_score_index=final_score,
        risk_level=level,
        contributing_factors=factors,
        checks=checks,
        cod_remains_available=True,
    )
