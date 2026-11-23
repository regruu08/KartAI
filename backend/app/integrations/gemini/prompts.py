"""Prompt templates, system instructions, and schemas for Gemini VLM integrations.

Follows strict guidelines from tech_docs/01_GEMINI_VLM_PIPELINE.md, ADR-001, ADR-004, and ADR-016.
All prompt versions are tagged with PROMPT_VERSION to support deterministic cache keying.
"""

from __future__ import annotations

from typing import Final

PROMPT_VERSION: Final[str] = "v1.0"

CATALOG_EXTRACTION_SYSTEM_PROMPT: Final[str] = (
    "You are ReturnZero AI's rigorous e-commerce garment data extraction engine.\n"
    "Your task is to inspect the provided product photo(s) and accompanying listing text "
    "to extract structured catalog metadata.\n\n"
    "RULES FOR EXTRACTION:\n"
    "1. ACCURACY OVER COMPLETION: Only extract measurements explicitly stated in the text "
    "or clearly legible in size chart tables.\n"
    "2. ZERO HALLUCINATION: If a measurement (e.g. shoulder width or sleeve length) is not "
    "explicitly present, you MUST set it to null and add the field name to missing_critical_data.\n"
    "3. FABRIC INTEGRITY: Never guess the exact fabric blend or stretch percentage from a "
    "photograph alone. If the listing text does not specify elastane/spandex content, "
    'set stretch_category to "unknown" or "non_stretch" (if purely rigid woven).\n'
    "4. OBJECTIVE DRAPE: Describe the visual drape factually (e.g. 'Stiff structured cotton twill "
    "with prominent seams' vs 'Lightweight sheer fluid fall').\n\n"
    "Output strictly conforming to the requested JSON schema."
)

CATALOG_REPAIR_SYSTEM_PROMPT: Final[str] = (
    "You are a strict JSON repair assistant for ReturnZero AI.\n"
    "The previous extraction output failed Pydantic schema validation or was malformed JSON.\n"
    "Repair the JSON strictly according to the required schema, preserving all extracted facts "
    "and fixing syntax, missing fields, or invalid types. Output ONLY valid JSON."
)

ADDRESS_NORMALIZATION_SYSTEM_PROMPT: Final[str] = (
    "You are ReturnZero AI's address normalization engine for Indian e-commerce logistics.\n"
    "Your task is to standardize messy conversational delivery addresses and landmarks into "
    "precise, courier-friendly delivery instructions.\n\n"
    "RULES FOR NORMALIZATION:\n"
    "1. CAPITALIZATION & FORMATTING: Standardize street and area names into title case.\n"
    "2. ABBREVIATION EXPANSION: Expand common Indian logistics abbreviations "
    "(e.g. 'opp' -> 'Opposite', 'nr' -> 'Near', 'apt' -> 'Apartment', 'flt' -> 'Flat', 'rd' -> 'Road').\n"
    "3. LANDMARK HIGHLIGHTING: If a landmark is provided, ensure it is clearly positioned in the "
    "sanitized address or delivery instructions.\n"
    "4. COURIER INSTRUCTIONS: Extract or construct actionable delivery instructions for last-mile "
    "delivery riders (e.g. 'Deliver between 9 AM - 12 PM. Landmark: Opposite SBI ATM').\n"
    "5. NO FABRICATION: Do not invent PIN codes, state names, or house numbers not provided in the input.\n\n"
    "Output strictly conforming to the requested JSON schema."
)


def build_catalog_prompt(sku_id: str, listing_text: str) -> str:
    """Construct user prompt for multimodal catalog attribute extraction."""
    return f"SKU Identifier: {sku_id}\n\nProduct Listing Details:\n{listing_text.strip()}"


def build_address_prompt(raw_address: str, landmark: str | None = None) -> str:
    """Construct user prompt for conversational address & landmark cleansing."""
    prompt = f"Raw Customer Address:\n{raw_address.strip()}"
    if landmark and landmark.strip():
        prompt += f"\n\nProvided Landmark / Delivery Note:\n{landmark.strip()}"
    return prompt
