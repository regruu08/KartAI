"""Pure address quality evaluation for ReturnZero AI.

Evaluates address completeness, house/flat identifiers, English and Hinglish
landmark tokens, and Indian 6-digit PIN format.
Shared by checkout risk scoring and the WhatsApp delivery assurance simulator.
Reference: ADR-003, ADR-015, AGENTS.md §5 (E3, E15) & §6.2.
"""

import re
from dataclasses import dataclass, field
from typing import Final, Literal

AddressStatus = Literal["Complete", "NeedsLandmark", "Poor"]

# Strict 6-digit Indian Postal Index Number (PIN) format
PIN_REGEX: Final[re.Pattern[str]] = re.compile(r"^\d{6}$")

# House / Flat / Plot / Door number identifier regex pattern
HOUSE_REGEX: Final[re.Pattern[str]] = re.compile(
    r"\b(?:"
    r"flat|room|apt|apartment|house|h\.?\s*no\.?|plot|door|bldg|building|villa|floor|shop|unit|block|#"
    r")\s*[:.-]?\s*[\w\d\-/]+"
    r"|\b\d{1,4}[a-zA-Z]?(?:[/-]\d{1,4})?\b",
    re.IGNORECASE,
)

# Comprehensive dictionary of English and Hinglish landmark and street locator tokens (ADR-003)
LANDMARK_TOKENS: Final[tuple[str, ...]] = (
    # Directional / proximity locators
    "near",
    "opp",
    "opposite",
    "behind",
    "beside",
    "adjacent",
    "close to",
    "front of",
    "in front of",
    "next to",
    # Places of worship
    "mandir",
    "temple",
    "masjid",
    "mosque",
    "gurudwara",
    "church",
    # Thoroughfares & street descriptors (English + Hinglish)
    "chowk",
    "rasta",
    "gali",
    "marg",
    "road",
    "rd",
    "street",
    "lane",
    "cross",
    "main road",
    "bypass",
    "circle",
    "circle road",
    "path",
    # Urban areas & enclaves
    "nagar",
    "colony",
    "phase",
    "sector",
    "enclave",
    "society",
    "mohalla",
    "residency",
    "apartments",
    "complex",
    "tower",
    "avenue",
    # Commercial & civic reference landmarks
    "market",
    "bazar",
    "bazaar",
    "station",
    "metro station",
    "railway station",
    "bus stand",
    "bus stop",
    "post office",
    "police station",
    "police chowki",
    "school",
    "college",
    "hospital",
    "dispensary",
    "bank",
    "atm",
    "petrol pump",
    "flyover",
    "bridge",
)


@dataclass(frozen=True)
class AddressQualityResult:
    status: AddressStatus
    is_valid_pin: bool
    has_house_identifier: bool
    has_landmark: bool
    matched_landmarks: list[str] = field(default_factory=list)
    reason: str = ""


def address_quality(address: str, pin: str) -> AddressQualityResult:
    """Evaluate address quality into Complete, NeedsLandmark, or Poor.

    Pure function with zero side effects. Follows ADR-003 and AGENTS.md §6.2.
    """
    clean_pin = pin.strip()
    is_pin_valid = bool(PIN_REGEX.match(clean_pin))

    if not is_pin_valid:
        return AddressQualityResult(
            status="Poor",
            is_valid_pin=False,
            has_house_identifier=False,
            has_landmark=False,
            matched_landmarks=[],
            reason="Invalid 6-digit Indian PIN code format.",
        )

    clean_address = address.strip()
    if len(clean_address) < 10:
        return AddressQualityResult(
            status="Poor",
            is_valid_pin=True,
            has_house_identifier=False,
            has_landmark=False,
            matched_landmarks=[],
            reason="Address is too brief to identify a physical delivery location.",
        )

    lower_addr = clean_address.lower()

    # 1. Check for house / flat / building identifier
    has_house = bool(HOUSE_REGEX.search(clean_address))

    # 2. Check for landmark tokens
    matched_tokens: list[str] = []
    for token in LANDMARK_TOKENS:
        # Match token as distinct word or phrase
        pattern = rf"\b{re.escape(token)}\b"
        if re.search(pattern, lower_addr):
            matched_tokens.append(token)

    has_landmark_token = len(matched_tokens) > 0

    # 3. Decision classification
    # Complete: valid PIN, house/flat identifier, at least one landmark token, length >= 15
    if is_pin_valid and has_house and has_landmark_token and len(clean_address) >= 15:
        return AddressQualityResult(
            status="Complete",
            is_valid_pin=True,
            has_house_identifier=True,
            has_landmark=True,
            matched_landmarks=matched_tokens,
            reason="Address includes verifiable premises number, directional landmark, and valid PIN.",
        )

    # NeedsLandmark: has house/flat number or recognized structure, but missing landmark token
    if is_pin_valid and has_house and not has_landmark_token:
        return AddressQualityResult(
            status="NeedsLandmark",
            is_valid_pin=True,
            has_house_identifier=True,
            has_landmark=False,
            matched_landmarks=[],
            reason="Address lacks a directional landmark or neighborhood locator for the courier.",
        )

    # NeedsLandmark: specifies a landmark but missing house/premises number
    if is_pin_valid and has_landmark_token and not has_house:
        return AddressQualityResult(
            status="NeedsLandmark",
            is_valid_pin=True,
            has_house_identifier=False,
            has_landmark=True,
            matched_landmarks=matched_tokens,
            reason="Address specifies a landmark but lacks a clear flat or premises number.",
        )

    # Fallback to Poor if neither house nor landmark identifiable
    return AddressQualityResult(
        status="Poor",
        is_valid_pin=True,
        has_house_identifier=False,
        has_landmark=False,
        matched_landmarks=[],
        reason="Address lacks essential building, floor, or street identifiers.",
    )
