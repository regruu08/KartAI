"""Reference brand sizing conversion matrices for ReturnZero AI.

Converts shopper known brand and size (Zara, H&M, Uniqlo) into estimated
human body circumference measurements (inches) across standard sizes (XS-XL).
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
    },
    "H&M": {
        "XS": {"chest": 33.5, "waist": 25.5, "shoulder": 14.8},
        "S": {"chest": 35.5, "waist": 27.5, "shoulder": 15.8},
        "M": {"chest": 38.0, "waist": 30.0, "shoulder": 16.8},
        "L": {"chest": 41.0, "waist": 33.5, "shoulder": 17.8},
        "XL": {"chest": 44.0, "waist": 37.0, "shoulder": 18.8},
    },
    "Uniqlo": {
        "XS": {"chest": 33.0, "waist": 25.0, "shoulder": 15.0},
        "S": {"chest": 35.0, "waist": 27.0, "shoulder": 16.0},
        "M": {"chest": 37.5, "waist": 29.5, "shoulder": 17.0},
        "L": {"chest": 40.0, "waist": 32.0, "shoulder": 18.0},
        "XL": {"chest": 43.0, "waist": 35.0, "shoulder": 19.0},
    },
}

SUPPORTED_BRANDS: Final[tuple[str, ...]] = ("Zara", "H&M", "Uniqlo")
SUPPORTED_SIZES: Final[tuple[str, ...]] = ("XS", "S", "M", "L", "XL")


def get_body_estimate(brand: str, size: str) -> dict[str, float] | None:
    """Retrieve calibrated body circumference estimates for a brand and size.

    Returns None if brand or size is not recognized.
    """
    brand_table = BRAND_BODY_ESTIMATES.get(brand)
    if not brand_table:
        return None
    return brand_table.get(size.upper())
