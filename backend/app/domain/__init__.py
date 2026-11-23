"""Pure domain models and mathematical invariant engines for ReturnZero AI.

Modules:
- money: Decimal-based currency utilities, floor rounding, safe arithmetic.
- sizing: Deterministic sizing recommendation engine, EOM rules, dynamic confidence.
- address: Pure address quality evaluation, English & Hinglish landmark parsing.
- risk: Explainable risk evaluator, frozen RiskConfig, 3-point checklist.
- incentive: Closed-form margin-safe prepaid incentive solver, anti-abuse controls.
- scenario: Pure 10,000-shipment financial scenario modeler with deck parity.
"""

from app.domain.address import (
    AddressQualityResult,
    AddressStatus,
    address_quality,
)
from app.domain.incentive import (
    IncentiveQuoteResult,
    ReasonCode,
    calculate_incentive_quote,
)
from app.domain.money import (
    floor_to_step,
    format_currency,
    percentage_of,
    quantize_currency,
    safe_add,
    safe_sub,
    to_decimal,
)
from app.domain.risk import (
    DEFAULT_RISK_CONFIG,
    CheckStatus,
    OrderReviewCheck,
    RiskConfig,
    RiskEvaluationResult,
    RiskLevel,
    evaluate_order_risk,
)
from app.domain.scenario import (
    ScenarioProjection,
    ScenarioResult,
    calculate_scenario,
)
from app.domain.sizing import (
    FitRecommendation,
    FitZoneDetail,
    recommend_size,
)

__all__ = [
    "AddressQualityResult",
    "AddressStatus",
    "CheckStatus",
    "DEFAULT_RISK_CONFIG",
    "FitRecommendation",
    "FitZoneDetail",
    "IncentiveQuoteResult",
    "OrderReviewCheck",
    "ReasonCode",
    "RiskConfig",
    "RiskEvaluationResult",
    "RiskLevel",
    "ScenarioProjection",
    "ScenarioResult",
    "address_quality",
    "calculate_incentive_quote",
    "calculate_scenario",
    "evaluate_order_risk",
    "floor_to_step",
    "format_currency",
    "percentage_of",
    "quantize_currency",
    "recommend_size",
    "safe_add",
    "safe_sub",
    "to_decimal",
]
