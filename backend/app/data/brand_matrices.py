"""Reference brand sizing conversion matrices for ReturnZero AI.

Converts shopper known brand and size (Zara, H&M, Uniqlo, Levi's, Marks & Spencer)
into estimated human body circumference measurements (inches) across standard sizes (XS-XXL).
Reference: tech_docs/04_DETERMINISTIC_SIZING_ENGINE.md §2 and ADR-004.
"""

from typing import Final

# Standard reference brands calibrated for Indian fashion e-commerce shoppers
BRAND_BODY_ESTIMATES: Final[dict[str, dict[str, dict[str, float]]]] = {
    "Zara": {
        "XS": {"chest": 34.0, "waist": 26.0, "shoulder": 15.0},
        "S": {"chest": 36.0, "waist": 28.0, "shoulder": 16.0},
        "M": {"chest": 38.0, "waist": 30.5, "shoulder": 17.0},
        "L": {"chest": 40.5, "waist": 33.0, "shoulder": 18.0},
        "XL": {"chest": 43.0, "waist": 36.0, "shoulder": 19.0},
        "XXL": {"chest": 45.5, "waist": 39.0, "shoulder": 19.8},
    },
    "H&M": {
        "XS": {"chest": 33.5, "waist": 25.5, "shoulder": 14.8},
        "S": {"chest": 35.5, "waist": 27.5, "shoulder": 15.8},
        "M": {"chest": 38.0, "waist": 30.0, "shoulder": 16.8},
        "L": {"chest": 41.0, "waist": 33.5, "shoulder": 17.8},
        "XL": {"chest": 44.0, "waist": 37.0, "shoulder": 18.8},
        "XXL": {"chest": 46.5, "waist": 40.0, "shoulder": 19.6},
    },
    "Uniqlo": {
        "XS": {"chest": 33.0, "waist": 25.0, "shoulder": 15.0},
        "S": {"chest": 35.0, "waist": 27.0, "shoulder": 16.0},
        "M": {"chest": 37.5, "waist": 29.5, "shoulder": 17.0},
        "L": {"chest": 40.0, "waist": 32.0, "shoulder": 18.0},
        "XL": {"chest": 43.0, "waist": 35.0, "shoulder": 19.0},
        "XXL": {"chest": 45.5, "waist": 38.0, "shoulder": 19.8},
    },
    "Levi's": {
        "XS": {"chest": 34.5, "waist": 26.5, "shoulder": 15.2},
        "S": {"chest": 36.5, "waist": 28.5, "shoulder": 16.2},
        "M": {"chest": 39.0, "waist": 31.5, "shoulder": 17.2},
        "L": {"chest": 41.5, "waist": 34.0, "shoulder": 18.2},
        "XL": {"chest": 44.5, "waist": 37.0, "shoulder": 19.2},
        "XXL": {"chest": 47.0, "waist": 40.0, "shoulder": 20.0},
    },
    "Marks & Spencer": {
        "XS": {"chest": 34.0, "waist": 26.5, "shoulder": 15.0},
        "S": {"chest": 36.0, "waist": 28.5, "shoulder": 16.0},
        "M": {"chest": 38.5, "waist": 31.0, "shoulder": 17.0},
        "L": {"chest": 41.0, "waist": 34.0, "shoulder": 18.0},
        "XL": {"chest": 44.0, "waist": 37.0, "shoulder": 19.0},
        "XXL": {"chest": 46.5, "waist": 39.5, "shoulder": 19.8},
    },
}

_BRAND_LOOKUP: Final[dict[str, str]] = {name.lower(): name for name in BRAND_BODY_ESTIMATES}
_BRAND_LOOKUP["levis"] = "Levi's"
_BRAND_LOOKUP["m&s"] = "Marks & Spencer"

SUPPORTED_BRANDS: Final[tuple[str, ...]] = (
    "Zara",
    "H&M",
    "Uniqlo",
    "Levi's",
    "Marks & Spencer",
)
SUPPORTED_SIZES: Final[tuple[str, ...]] = ("XS", "S", "M", "L", "XL", "XXL")


def get_body_estimate(brand: str, size: str) -> dict[str, float] | None:
    """Retrieve calibrated body circumference estimates for a brand and size.

    Returns None if brand or size is not recognized.
    """
    canonical_brand = _BRAND_LOOKUP.get(brand.strip().lower())
    if not canonical_brand:
        return None
    return BRAND_BODY_ESTIMATES[canonical_brand].get(size.strip().upper())
