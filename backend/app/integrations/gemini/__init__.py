"""Gemini VLM Integrations Package for ReturnZero AI.

Follows ADR-001 (E1): All Google GenAI SDK imports are strictly confined to adapter.py.
"""

from app.integrations.gemini.adapter import (
    AddressNormalizerProtocol,
    CatalogExtractorProtocol,
    CircuitBreaker,
    CircuitBreakerOpenException,
    GeminiAdapter,
    GeminiAPIException,
)
from app.integrations.gemini.cache import (
    CatalogCache,
    get_catalog_cache,
)
from app.integrations.gemini.extractor import (
    CatalogExtractor,
    preprocess_image,
)
from app.integrations.gemini.normalizer import (
    AddressNormalizer,
    clean_address_text,
    deterministic_fallback_normalize,
)
from app.integrations.gemini.prompts import (
    ADDRESS_NORMALIZATION_SYSTEM_PROMPT,
    CATALOG_EXTRACTION_SYSTEM_PROMPT,
    CATALOG_REPAIR_SYSTEM_PROMPT,
    PROMPT_VERSION,
    build_address_prompt,
    build_catalog_prompt,
)

__all__ = [
    "ADDRESS_NORMALIZATION_SYSTEM_PROMPT",
    "AddressNormalizer",
    "AddressNormalizerProtocol",
    "CATALOG_EXTRACTION_SYSTEM_PROMPT",
    "CATALOG_REPAIR_SYSTEM_PROMPT",
    "CatalogCache",
    "CatalogExtractor",
    "CatalogExtractorProtocol",
    "CircuitBreaker",
    "CircuitBreakerOpenException",
    "GeminiAdapter",
    "GeminiAPIException",
    "PROMPT_VERSION",
    "build_address_prompt",
    "build_catalog_prompt",
    "clean_address_text",
    "deterministic_fallback_normalize",
    "get_catalog_cache",
    "preprocess_image",
]
