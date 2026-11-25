"""Conversational Address Normalizer & Landmark Cleansing Service for ReturnZero AI.

Transforms conversational, messy Indian street addresses and landmark notes into
clean, standardized postal strings and actionable courier delivery instructions.
Features 100% offline deterministic rule-based fallback per ADR-003, ADR-015, and ADR-016.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from pydantic import ValidationError

from app.config import Settings
from app.integrations.gemini.adapter import (
    AddressNormalizerProtocol,
    CircuitBreakerOpenException,
    GeminiAdapter,
    GeminiAPIException,
)
from app.integrations.gemini.prompts import (
    ADDRESS_NORMALIZATION_SYSTEM_PROMPT,
    build_address_prompt,
)
from app.schemas.api_contracts import (
    GeminiAddressNormalizationPayload,
    NormalizedAddressResult,
)

logger = logging.getLogger("returnzero.integrations.gemini.normalizer")

# Common Indian logistics abbreviation expansion map
ABBREVIATION_MAP: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(opp\.?|oppo\.?)\b", re.IGNORECASE), "Opposite"),
    (re.compile(r"\b(nr\.?|near to)\b", re.IGNORECASE), "Near"),
    (re.compile(r"\b(rd\.?)\b", re.IGNORECASE), "Road"),
    (re.compile(r"\b(apt\.?|apts\.?)\b", re.IGNORECASE), "Apartment"),
    (re.compile(r"\b(flt\.?)\b", re.IGNORECASE), "Flat"),
    (re.compile(r"\b(bldg\.?)\b", re.IGNORECASE), "Building"),
    (re.compile(r"\b(h\.?\s*no\.?|hno\.?)\b", re.IGNORECASE), "House No."),
    (re.compile(r"\b(sec\.?)\b", re.IGNORECASE), "Sector"),
    (re.compile(r"\b(plt\.?)\b", re.IGNORECASE), "Plot"),
    (re.compile(r"\b(st\.?)\b", re.IGNORECASE), "Street"),
    (re.compile(r"\b(mkt\.?)\b", re.IGNORECASE), "Market"),
    (re.compile(r"\b(col\.?)\b", re.IGNORECASE), "Colony"),
    (re.compile(r"\b(ph\.?)\b", re.IGNORECASE), "Phase"),
    (re.compile(r"\b(soc\.?)\b", re.IGNORECASE), "Society"),
    (re.compile(r"\b(ext\.?)\b", re.IGNORECASE), "Extension"),
]


def clean_address_text(text: str) -> str:
    """Standardize spacing, title-case words, and expand abbreviations."""
    cleaned = text.strip()
    if not cleaned:
        return ""

    # Expand known abbreviations
    for pattern, replacement in ABBREVIATION_MAP:
        cleaned = pattern.sub(replacement, cleaned)

    # Clean multiple spaces and comma punctuation
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\s*,\s*", ", ", cleaned)
    cleaned = re.sub(r",+", ",", cleaned).strip(", ")

    # Title-case words while preserving alphanumeric codes like 3B, 402, 14/2
    parts = cleaned.split(" ")
    formatted_words: list[str] = []
    for word in parts:
        # If word has digits or special chars, preserve case or capitalize letters
        if any(char.isdigit() for char in word):
            formatted_words.append(word.upper())
        elif len(word) <= 2 and word.lower() in ("to", "of", "in", "at", "by", "on"):
            formatted_words.append(word.lower())
        else:
            formatted_words.append(word.capitalize())

    return " ".join(formatted_words)


def deterministic_fallback_normalize(
    raw_address: str,
    landmark: str | None = None,
) -> NormalizedAddressResult:
    """100% offline deterministic rule-based address normalizer.

    Guarantees simulator and verification flows continue working under
    total network isolation or zero AI quota.
    """
    cleaned_address = clean_address_text(raw_address)
    cleaned_landmark = clean_address_text(landmark) if landmark and landmark.strip() else None

    # Construct standardized full address
    if cleaned_landmark:
        # Check if landmark is already incorporated in the address string
        if cleaned_landmark.lower() not in cleaned_address.lower():
            sanitized_address = f"{cleaned_address}, Landmark: {cleaned_landmark}"
        else:
            sanitized_address = cleaned_address
        delivery_instructions = f"Deliver to address. Landmark: {cleaned_landmark}."
    else:
        sanitized_address = cleaned_address
        delivery_instructions = "Contact customer upon arrival. Deliver to address."

    return NormalizedAddressResult(
        sanitized_address=sanitized_address,
        landmark=cleaned_landmark,
        delivery_instructions=delivery_instructions,
        confidence="medium",
        provenance="deterministic_rule",
    )


class AddressNormalizer(AddressNormalizerProtocol):
    """Conversational address & landmark cleansing service with offline fallback."""

    def __init__(
        self,
        adapter: GeminiAdapter | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.adapter = adapter if adapter is not None else GeminiAdapter(settings=settings)

    async def normalize(
        self,
        raw_address: str,
        landmark: str | None = None,
    ) -> NormalizedAddressResult:
        """Cleanse raw address using Gemini structured output with deterministic fallback."""
        if not raw_address or not raw_address.strip():
            return deterministic_fallback_normalize(raw_address, landmark)

        # Attempt live Gemini structured output
        try:
            prompt = build_address_prompt(raw_address, landmark)
            contents: list[Any] = [prompt]

            raw_text, _ = await self.adapter.generate_content(
                contents=contents,
                system_instruction=ADDRESS_NORMALIZATION_SYSTEM_PROMPT,
                response_schema=GeminiAddressNormalizationPayload,
                temperature=0.1,
            )

            parsed_payload = GeminiAddressNormalizationPayload.model_validate_json(raw_text)
            result = NormalizedAddressResult(
                **parsed_payload.model_dump(),
                provenance="live_gemini",
            )
            logger.info("[ADDRESS NORMALIZER] Live cleansing success via %s", self.adapter.model_id)
            return result

        except (CircuitBreakerOpenException, GeminiAPIException, ValidationError, Exception) as exc:
            logger.info(
                "[ADDRESS NORMALIZER] Live normalizer unavailable (%s: %s). Running deterministic fallback.",
                type(exc).__name__,
                exc,
            )

        # Seamless offline deterministic fallback
        return deterministic_fallback_normalize(raw_address, landmark)
