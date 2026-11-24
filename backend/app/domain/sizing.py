"""Deterministic sizing recommendation engine for ReturnZero AI.

Evaluates shopper body measurements (derived via brand conversion or exact inputs)
against garment pattern dimensions and fabric elasticity using calibrated
Ease-Over-Measurement (EOM) rules.
Reference: ADR-004, AGENTS.md §5 (E4, E13) & §6.2.
"""

from dataclasses import dataclass, field
from typing import Any, Final

from app.data.brand_matrices import BRAND_BODY_ESTIMATES, get_body_estimate

# Desired chest ease allowances across all 4 customer preferences (ADR-004)
EASE_TIGHT: Final[float] = 1.0  # Snug / form-fitting
EASE_TAILORED: Final[float] = 2.5  # Regular / classic tailored fit
EASE_RELAXED: Final[float] = 4.0  # Casual / breezy ease
EASE_OVERSIZED: Final[float] = 6.0  # Modern streetwear / exaggerated silhouette

DESIRED_EASE_BY_PREFERENCE: Final[dict[str, float]] = {
    "tight": EASE_TIGHT,
    "tailored": EASE_TAILORED,
    "regular": EASE_TAILORED,  # UI label alias per deck
    "relaxed": EASE_RELAXED,
    "oversized": EASE_OVERSIZED,
}

# Desired shoulder ease allowances across customer preferences (ADR-004)
DESIRED_SHOULDER_EASE_BY_PREFERENCE: Final[dict[str, float]] = {
    "tight": 0.25,
    "tailored": 0.5,
    "regular": 0.5,  # UI label alias per deck
    "relaxed": 1.0,
    "oversized": 2.0,
}
DESIRED_SHOULDER_EASE: Final[float] = 0.5

# Ease-Over-Measurement (EOM) bounds per stretch class (ADR-004)
# (min_chest_ease, max_chest_ease, min_shoulder_ease, max_shoulder_ease, hard_floor_chest, hard_floor_shoulder)
EOM_RULES: Final[dict[str, dict[str, float]]] = {
    "non_stretch": {
        "min_chest_ease": 2.0,
        "max_chest_ease": 3.5,
        "min_shoulder_ease": 0.5,
        "max_shoulder_ease": 1.0,
        "hard_floor_chest": 1.0,
        "hard_floor_shoulder": 0.0,
    },
    "slight_stretch": {
        "min_chest_ease": 1.0,
        "max_chest_ease": 2.0,
        "min_shoulder_ease": 0.0,
        "max_shoulder_ease": 0.5,
        "hard_floor_chest": 0.0,
        "hard_floor_shoulder": -0.5,
    },
    "medium_stretch": {
        "min_chest_ease": 0.0,
        "max_chest_ease": 1.5,
        "min_shoulder_ease": -0.25,
        "max_shoulder_ease": 0.25,
        "hard_floor_chest": -1.0,
        "hard_floor_shoulder": -0.75,
    },
    "high_stretch": {
        "min_chest_ease": -1.0,
        "max_chest_ease": 1.0,
        "min_shoulder_ease": -0.5,
        "max_shoulder_ease": 0.5,
        "hard_floor_chest": -2.0,
        "hard_floor_shoulder": -1.0,
    },
}

# Curated reference catalog for the 4 core fashion SKUs (ADR-013)
CURATED_SKUS: Final[dict[str, dict[str, Any]]] = {
    "SKU-01": {
        "id": "SKU-01",
        "name": "Handcrafted Chanderi Silk Anarkali Kurta",
        "fabric_stretch": "non_stretch",
        "has_shoulder": True,
        "has_sleeve": True,
        "length_inches": 48.0,
        "sizes": {
            "S": {"chest": 36.0, "waist": 32.0, "shoulder": 14.5, "length": 46.0},
            "M": {"chest": 38.0, "waist": 34.0, "shoulder": 15.5, "length": 47.0},
            "L": {"chest": 40.0, "waist": 36.0, "shoulder": 17.0, "length": 48.0},
            "XL": {"chest": 42.0, "waist": 38.0, "shoulder": 18.0, "length": 49.0},
        },
    },
    "SKU-02": {
        "id": "SKU-02",
        "name": "Relaxed Mandarin Collar Linen Shirt",
        "fabric_stretch": "slight_stretch",
        "has_shoulder": True,
        "has_sleeve": True,
        "length_inches": 29.0,
        "sizes": {
            "S": {"chest": 38.0, "waist": 36.0, "shoulder": 16.5, "length": 28.0},
            "M": {"chest": 40.0, "waist": 38.0, "shoulder": 17.5, "length": 29.0},
            "L": {"chest": 42.0, "waist": 40.0, "shoulder": 18.5, "length": 30.0},
            "XL": {"chest": 44.0, "waist": 42.0, "shoulder": 19.5, "length": 31.0},
        },
    },
    "SKU-03": {
        "id": "SKU-03",
        "name": "Raw Indigo Denim Trucker Jacket",
        "fabric_stretch": "non_stretch",
        "has_shoulder": True,
        "has_sleeve": False,  # Intentionally missing sleeve measurement (ADR-004, ADR-013)
        "length_inches": 26.0,
        "sizes": {
            "S": {"chest": 40.0, "waist": 38.0, "shoulder": 17.0, "length": 25.0},
            "M": {"chest": 42.0, "waist": 40.0, "shoulder": 18.0, "length": 26.0},
            "L": {"chest": 44.0, "waist": 42.0, "shoulder": 19.0, "length": 27.0},
            "XL": {"chest": 46.0, "waist": 44.0, "shoulder": 20.0, "length": 28.0},
        },
    },
    "SKU-04": {
        "id": "SKU-04",
        "name": "Flowy Floral Rayon Tiered Maxi Dress",
        "fabric_stretch": "slight_stretch",
        "has_shoulder": True,
        "has_sleeve": True,
        "length_inches": 53.0,
        "sizes": {
            "S": {"chest": 34.0, "waist": 26.0, "shoulder": 14.0, "length": 52.0},
            "M": {"chest": 36.0, "waist": 28.0, "shoulder": 15.0, "length": 53.0},
            "L": {"chest": 38.0, "waist": 30.0, "shoulder": 16.0, "length": 54.0},
            "XL": {"chest": 40.0, "waist": 32.0, "shoulder": 17.0, "length": 55.0},
        },
    },
}

# Alias mapping for alternate SKU identifiers
SKU_ALIASES: Final[dict[str, str]] = {
    "SKU-CHANDERI-01": "SKU-01",
    "SKU-LINEN-02": "SKU-02",
    "SKU-DENIM-03": "SKU-03",
    "SKU-DRESS-04": "SKU-04",
}


@dataclass(frozen=True)
class FitZoneDetail:
    shopper_inches: float
    garment_inches: float
    ease_inches: float
    status: str


@dataclass(frozen=True)
class FitRecommendation:
    sku_id: str
    recommended_size: str
    confidence_level: str  # "High" | "Medium" | "Low (Insufficient Data)"
    fit_score: int  # Explicitly documented as heuristic index (0-100)
    fit_zone_breakdown: dict[str, Any]
    explanation_text: str
    missing_data_warnings: list[str] = field(default_factory=list)


def _resolve_sku_spec(
    sku_id: str, custom_catalog: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Resolve SKU spec from custom or curated catalog, handling aliases."""
    normalized_id = SKU_ALIASES.get(sku_id, sku_id)
    if custom_catalog and normalized_id in custom_catalog:
        return custom_catalog[normalized_id]  # type: ignore[no-any-return]
    if custom_catalog and sku_id in custom_catalog:
        return custom_catalog[sku_id]  # type: ignore[no-any-return]
    return CURATED_SKUS.get(normalized_id)


def _calculate_height_note(
    height_cm: float | None, length_inches: float | None
) -> tuple[str | None, str | None]:
    """Generate height fit commentary or missing length warning."""
    if height_cm is None:
        return None, None
    if length_inches is None:
        return (
            None,
            "Shopper height provided but garment length is not specified in merchant catalog.",
        )

    if length_inches >= 48.0:
        return (
            f'Garment length {length_inches:.1f}" provides ankle/floor length for height {int(height_cm)} cm.',
            None,
        )
    if length_inches >= 36.0:
        return (
            f'Garment length {length_inches:.1f}" falls at or below the knee for height {int(height_cm)} cm.',
            None,
        )
    return (
        f'Garment length {length_inches:.1f}" provides mid-hip length for height {int(height_cm)} cm.',
        None,
    )


def recommend_size(
    sku_id: str,
    known_brand: str,
    known_size: str,
    fit_preference: str = "tailored",
    height_cm: float | None = None,
    chest_inches: float | None = None,
    waist_inches: float | None = None,
    custom_catalog: dict[str, Any] | None = None,
) -> FitRecommendation:
    """Deterministically compute size recommendation based on body estimates and garment specs.

    Pure function with zero side-effects. Follows ADR-004 and AGENTS.md §6.2.
    """
    sku = _resolve_sku_spec(sku_id, custom_catalog)
    normalized_pref = fit_preference.strip().lower()
    desired_ease = DESIRED_EASE_BY_PREFERENCE.get(normalized_pref, EASE_TAILORED)

    # 1. Handle Unknown SKU or Missing Pattern Data
    if not sku or "sizes" not in sku or not sku["sizes"]:
        return FitRecommendation(
            sku_id=sku_id,
            recommended_size=known_size.upper(),
            confidence_level="Low (Insufficient Data)",
            fit_score=50,
            fit_zone_breakdown={"overall": "Standard (Catalog data unavailable)"},
            explanation_text="SKU measurements unavailable in merchant catalog. Suggested standard size based on known size.",
            missing_data_warnings=[
                "Merchant has not provided verified pattern measurement tables for this garment."
            ],
        )

    # 2. Resolve shopper body measurements
    warnings: list[str] = []
    body_ref = get_body_estimate(known_brand, known_size)
    brand_recognized = body_ref is not None

    if not body_ref:
        # Fallback to standard Zara reference if brand unknown
        body_ref = BRAND_BODY_ESTIMATES["Zara"].get(
            known_size.upper(), {"chest": 38.0, "waist": 30.5, "shoulder": 17.0}
        )
        warnings.append(
            f"Brand '{known_brand}' not in verified conversion matrix. Calibrated via Zara reference."
        )

    target_chest = chest_inches if chest_inches is not None else body_ref["chest"]
    target_waist = waist_inches if waist_inches is not None else body_ref["waist"]
    target_shoulder = body_ref["shoulder"]

    # Check for missing SKU dimensions
    has_shoulder_dims = sku.get("has_shoulder", True)
    if not has_shoulder_dims:
        warnings.append(
            "[Notice: Sizing calibrated via chest circumference; shoulder width not specified by merchant]"
        )

    has_sleeve_dims = sku.get("has_sleeve", True)
    if not has_sleeve_dims:
        warnings.append(
            "[Note: Sleeve length not specified by merchant; sizing calibrated via chest & shoulder circumference]"
        )

    # Height evaluation
    garment_len = sku.get("length_inches")
    height_note, height_warn = _calculate_height_note(height_cm, garment_len)
    if height_warn:
        warnings.append(height_warn)

    # 3. Evaluate sizes against EOM rules and penalty matrix
    stretch = sku.get("fabric_stretch", "non_stretch")
    rules = EOM_RULES.get(stretch, EOM_RULES["non_stretch"])
    hard_floor_chest = rules["hard_floor_chest"]
    hard_floor_shoulder = rules["hard_floor_shoulder"]

    penalties: dict[str, float] = {}
    breakdowns: dict[str, dict[str, Any]] = {}
    eliminated_rigid_sizes: list[tuple[str, float, float]] = []

    for size_label, dims in sku["sizes"].items():
        g_chest = dims.get("chest", 0.0)
        g_shoulder = dims.get("shoulder", target_shoulder if not has_shoulder_dims else 0.0)
        g_waist = dims.get("waist")

        chest_ease = g_chest - target_chest
        shoulder_ease = g_shoulder - target_shoulder

        # Eliminate sizes violating hard negative-ease floors for rigid fabrics (ADR-004)
        if chest_ease < hard_floor_chest or (
            has_shoulder_dims and shoulder_ease < hard_floor_shoulder
        ):
            if (
                has_shoulder_dims
                and shoulder_ease < hard_floor_shoulder
                and stretch == "non_stretch"
            ):
                eliminated_rigid_sizes.append((size_label, shoulder_ease, hard_floor_shoulder))
            continue

        # Penalties: chest ease deviation + shoulder ease deviation + waist ease deviation
        chest_pen = abs(chest_ease - desired_ease)
        desired_shoulder_ease = DESIRED_SHOULDER_EASE_BY_PREFERENCE.get(
            normalized_pref, DESIRED_SHOULDER_EASE
        )
        shoulder_weight = 1.0 if normalized_pref in ("relaxed", "oversized") else 2.0
        shoulder_pen = (
            (abs(shoulder_ease - desired_shoulder_ease) * shoulder_weight)
            if has_shoulder_dims
            else 0.0
        )

        waist_pen = 0.0
        if g_waist is not None:
            waist_ease = g_waist - target_waist
            # Waist desired ease is slightly more generous for comfortable drape
            desired_waist_ease = max(2.0, desired_ease)
            waist_weight = 0.25 if normalized_pref in ("relaxed", "oversized") else 0.5
            waist_pen = abs(waist_ease - desired_waist_ease) * waist_weight

        total_penalty = chest_pen + shoulder_pen + waist_pen
        penalties[size_label] = total_penalty

        # Generate zone breakdowns
        chest_status = (
            "comfortable" if 1.5 <= chest_ease <= 3.5 else "fitted" if chest_ease < 1.5 else "roomy"
        )
        shoulder_status = (
            "comfortable"
            if shoulder_ease >= 0.5
            else "snug"
            if shoulder_ease >= 0.0
            else "restrictive"
        )
        waist_status = "relaxed" if (g_waist and (g_waist - target_waist) >= 2.0) else "fitted"

        zone_bd: dict[str, Any] = {
            "bust": FitZoneDetail(
                shopper_inches=target_chest,
                garment_inches=g_chest,
                ease_inches=round(chest_ease, 2),
                status=chest_status,
            ).__dict__,
            "waist": FitZoneDetail(
                shopper_inches=target_waist,
                garment_inches=g_waist if g_waist else 0.0,
                ease_inches=round((g_waist - target_waist) if g_waist else 0.0, 2),
                status=waist_status,
            ).__dict__,
        }
        if has_shoulder_dims:
            zone_bd["shoulder"] = FitZoneDetail(
                shopper_inches=target_shoulder,
                garment_inches=g_shoulder,
                ease_inches=round(shoulder_ease, 2),
                status=shoulder_status,
            ).__dict__
        if height_note:
            zone_bd["length"] = {"note": height_note}

        breakdowns[size_label] = zone_bd

    # Generate rigid-fabric shoulder note from data (ADR-004 / A3)
    rigid_fabric_note: str | None = None
    if eliminated_rigid_sizes:
        # Focus on explaining the shopper's reference size if eliminated, or all eliminated sizes
        known_sz_upper = known_size.upper()
        focus_eliminated = [item for item in eliminated_rigid_sizes if item[0] == known_sz_upper]
        items_to_report = focus_eliminated if focus_eliminated else eliminated_rigid_sizes
        notes = [
            f'Size {sz} eliminated: shoulder ease {ease:+.1f}" is below the {floor:.1f}" minimum for non-stretch fabric.'
            for sz, ease, floor in items_to_report
        ]
        rigid_fabric_note = " ".join(notes)

    # 4. Determine recommendation
    if penalties:
        # Sort sizes by lowest penalty
        sorted_sizes = sorted(penalties.items(), key=lambda x: x[1])
        best_size, best_penalty = sorted_sizes[0]
        runner_up_penalty = sorted_sizes[1][1] if len(sorted_sizes) > 1 else None
    else:
        # Fallback to largest size if all failed hard non-stretch thresholds
        best_size = list(sku["sizes"].keys())[-1]
        best_penalty = 10.0
        runner_up_penalty = None
        breakdowns[best_size] = {
            "overall": "Maximum available size recommended (garment pattern runs small)"
        }

    # Attach rigid fabric note to breakdowns for explainability
    if rigid_fabric_note and best_size in breakdowns:
        breakdowns[best_size]["shoulders"] = {"note": rigid_fabric_note}

    # 5. Dynamic Categorical Confidence Calculation with explicit data-gap caps (ADR-004 / A3)
    confidence_scale = ["Low (Insufficient Data)", "Medium", "High"]

    def _min_band(band_a: str, band_b: str) -> str:
        idx_a = confidence_scale.index(band_a) if band_a in confidence_scale else 0
        idx_b = confidence_scale.index(band_b) if band_b in confidence_scale else 0
        return confidence_scale[min(idx_a, idx_b)]

    if best_penalty <= 2.5:
        base_confidence = "High"
    elif best_penalty <= 4.5:
        base_confidence = "Medium"
    else:
        base_confidence = "Low (Insufficient Data)"

    # Formulate list of data-gap caps
    gap_caps: list[str] = []
    if not brand_recognized:
        gap_caps.append("Medium")
    if not has_shoulder_dims:
        gap_caps.append("Medium")
    if not has_sleeve_dims:
        gap_caps.append("Medium")
    if stretch == "unknown":
        gap_caps.append("Medium")
    if (
        runner_up_penalty is not None
        and (runner_up_penalty - best_penalty) < 0.25
        and stretch == "non_stretch"
    ):
        gap_caps.append("Medium")

    confidence = base_confidence
    for cap in gap_caps:
        confidence = _min_band(confidence, cap)

    # Heuristic fit score in [50, 95] for explainability
    fit_score = max(50, min(95, int(95 - (best_penalty * 8))))

    # 6. Construct human explanation
    garment_title = sku.get("name", sku_id)
    explanation = (
        f"Based on your {known_brand} Size {known_size.upper()}, we recommend Size {best_size} "
        f"in this {garment_title} for a {normalized_pref} fit in {stretch.replace('_', ' ')} fabric."
    )
    if rigid_fabric_note:
        explanation += f" {rigid_fabric_note}"
    if height_note:
        explanation += f" {height_note}"

    return FitRecommendation(
        sku_id=sku_id,
        recommended_size=best_size,
        confidence_level=confidence,
        fit_score=fit_score,
        fit_zone_breakdown=breakdowns.get(best_size, {}),
        explanation_text=explanation,
        missing_data_warnings=warnings,
    )
