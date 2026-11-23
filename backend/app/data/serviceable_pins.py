"""Synthetic serviceable pincode registry and high-risk demo lanes.

NOTE: This is a synthetic demo lane list for hackathon demonstration and testing
purposes only (per ADR-003 and AGENTS.md §5). It does not represent live courier feeds.
"""

from typing import Final, NamedTuple


class PinMetadata(NamedTuple):
    city: str
    state: str
    tier: str  # "Tier-1", "Tier-2", "Tier-3"
    is_high_risk: bool


# Synthetic serviceable pincodes demarcated by tier and operational risk
SYNTHETIC_SERVICEABLE_PINS: Final[dict[str, PinMetadata]] = {
    # Tier-1 Metro lanes (Standard delivery, low transit failure)
    "110001": PinMetadata(city="Delhi", state="Delhi", tier="Tier-1", is_high_risk=False),
    "110020": PinMetadata(city="Delhi", state="Delhi", tier="Tier-1", is_high_risk=False),
    "400001": PinMetadata(city="Mumbai", state="Maharashtra", tier="Tier-1", is_high_risk=False),
    "400050": PinMetadata(city="Mumbai", state="Maharashtra", tier="Tier-1", is_high_risk=False),
    "560001": PinMetadata(city="Bengaluru", state="Karnataka", tier="Tier-1", is_high_risk=False),
    "560034": PinMetadata(city="Bengaluru", state="Karnataka", tier="Tier-1", is_high_risk=False),
    "600001": PinMetadata(city="Chennai", state="Tamil Nadu", tier="Tier-1", is_high_risk=False),
    "700001": PinMetadata(city="Kolkata", state="West Bengal", tier="Tier-1", is_high_risk=False),
    "500001": PinMetadata(city="Hyderabad", state="Telangana", tier="Tier-1", is_high_risk=False),
    # Tier-2 Cities (Moderate delivery failure rate)
    "302001": PinMetadata(city="Jaipur", state="Rajasthan", tier="Tier-2", is_high_risk=True),
    "226001": PinMetadata(city="Lucknow", state="Uttar Pradesh", tier="Tier-2", is_high_risk=True),
    "452001": PinMetadata(city="Indore", state="Madhya Pradesh", tier="Tier-2", is_high_risk=True),
    "411001": PinMetadata(city="Pune", state="Maharashtra", tier="Tier-2", is_high_risk=False),
    "380001": PinMetadata(city="Ahmedabad", state="Gujarat", tier="Tier-2", is_high_risk=False),
    # Tier-3 & Remote Clusters (High historical transit failure demo lanes per ADR-003)
    "143001": PinMetadata(city="Amritsar", state="Punjab", tier="Tier-3", is_high_risk=True),
    "151001": PinMetadata(city="Bhatinda", state="Punjab", tier="Tier-3", is_high_risk=True),
    "276001": PinMetadata(city="Azamgarh", state="Uttar Pradesh", tier="Tier-3", is_high_risk=True),
    "301001": PinMetadata(city="Alwar", state="Rajasthan", tier="Tier-3", is_high_risk=True),
}

# Frozen set of synthetic high-risk PINs for rapid O(1) risk evaluation
SYNTHETIC_HIGH_RISK_PINS: Final[frozenset[str]] = frozenset(
    pin for pin, meta in SYNTHETIC_SERVICEABLE_PINS.items() if meta.is_high_risk
)

# Frozen set of all synthetic serviceable PINs
ALL_SERVICEABLE_PINS: Final[frozenset[str]] = frozenset(SYNTHETIC_SERVICEABLE_PINS.keys())


def is_serviceable_pin(pin: str) -> bool:
    """Check if PIN is within the synthetic serviceable logistics network."""
    return pin in ALL_SERVICEABLE_PINS


def is_high_risk_pin(pin: str) -> bool:
    """Check if PIN belongs to synthetic high-risk transit failure lanes."""
    return pin in SYNTHETIC_HIGH_RISK_PINS


def get_pin_metadata(pin: str) -> PinMetadata | None:
    """Retrieve city, state, and tier metadata for a synthetic PIN."""
    return SYNTHETIC_SERVICEABLE_PINS.get(pin)
