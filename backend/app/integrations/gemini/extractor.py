"""Multimodal Catalog Extraction Service for ReturnZero AI.

Executes 3-tier extraction:
1. In-memory TTL Cache (0 duplicate calls)
2. Live Google Gemini 3.8 Flash Multimodal API (with downscaled JPEG and schema enforcement)
3. Pre-computed Verified Benchmark Fixture Fallback (100% demo uptime guarantee)

Reference: ADR-001, ADR-004, ADR-006, ADR-013, ADR-016.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image
from pydantic import ValidationError

from app.config import Settings
from app.domain.sizing import CURATED_SKUS
from app.integrations.gemini.adapter import (
    CatalogExtractorProtocol,
    CircuitBreakerOpenException,
    GeminiAdapter,
    GeminiAPIException,
)
from app.integrations.gemini.cache import CatalogCache, get_catalog_cache
from app.integrations.gemini.prompts import (
    CATALOG_EXTRACTION_SYSTEM_PROMPT,
    CATALOG_REPAIR_SYSTEM_PROMPT,
    PROMPT_VERSION,
    build_catalog_prompt,
)
from app.schemas.api_contracts import (
    ExtractedCatalogAttributes,
    GarmentMeasurements,
    GeminiCatalogExtractionPayload,
    ProvenanceEnum,
)

logger = logging.getLogger("returnzero.integrations.gemini.extractor")

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "fixtures"

# Baseline listing texts for the 4 curated demo SKUs
DEFAULT_LISTING_TEXTS: dict[str, str] = {
    "SKU-01": (
        "Handcrafted Chanderi Silk Anarkali Kurta. 100% Chanderi Silk, zero-stretch (0% elastane), "
        "structured bodice, 180 GSM. Concealed side zipper. Size chart: "
        "S: Bust 36, Waist 32, Hip 40, Shoulder 14.5, Length 46. "
        "M: Bust 38, Waist 34, Hip 42, Shoulder 15.5, Length 47. "
        "L: Bust 40, Waist 36, Hip 44, Shoulder 17.0, Length 48. "
        "XL: Bust 42, Waist 38, Hip 46, Shoulder 18.0, Length 49."
    ),
    "SKU-02": (
        "Relaxed Mandarin Collar Linen Shirt. 70% Cotton / 30% Linen, slight natural give, relaxed drape, "
        "160 GSM. Front button placket. Size chart: "
        "S: Chest 38, Waist 36, Shoulder 16.5, Length 28. "
        "M: Chest 40, Waist 38, Shoulder 17.5, Length 29. "
        "L: Chest 42, Waist 40, Shoulder 18.5, Length 30. "
        "XL: Chest 44, Waist 42, Shoulder 19.5, Length 31."
    ),
    "SKU-03": (
        "Raw Indigo Denim Trucker Jacket. 99% Cotton / 1% Spandex, 320 GSM, rigid armholes. "
        "Metal shank button placket. Size chart: "
        "S: Chest 40, Waist 38, Shoulder 17.0, Length 25. "
        "M: Chest 42, Waist 40, Shoulder 18.0, Length 26. "
        "L: Chest 44, Waist 42, Shoulder 19.0, Length 27. "
        "XL: Chest 46, Waist 44, Shoulder 20.0, Length 28. "
        "Note: Sleeve length is unstated in merchant specifications."
    ),
    "SKU-04": (
        "Flowy Floral Rayon Tiered Maxi Dress. 100% Viscose Rayon, highly fluid drape, elasticated smocked waist. "
        "Pullover styling. Size chart: "
        "S: Bust 34, Waist 26, Shoulder 14.0, Length 52. "
        "M: Bust 36, Waist 28, Shoulder 15.0, Length 53. "
        "L: Bust 38, Waist 30, Shoulder 16.0, Length 54. "
        "XL: Bust 40, Waist 32, Shoulder 17.0, Length 55."
    ),
}


def preprocess_image(
    image_input: str | bytes | Path | Image.Image,
    max_dimension: int = 1024,
    jpeg_quality: int = 85,
) -> tuple[bytes, str, Image.Image]:
    """Preprocess image: resize to max <= 1024px, convert to RGB JPEG, compute SHA-256.

    Returns tuple of: (preprocessed_jpeg_bytes, sha256_hex_digest, pil_image).
    """
    if isinstance(image_input, Image.Image):
        img = image_input
    elif isinstance(image_input, (str, Path)):
        img = Image.open(image_input)
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    # Normalize color mode to RGB
    if img.mode in ("RGBA", "P", "LA", "CMYK"):
        img = img.convert("RGB")

    # Downscale if exceeding max dimension (preserving aspect ratio)
    if img.width > max_dimension or img.height > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

    # Save to JPEG buffer
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
    jpeg_bytes = buf.getvalue()
    image_sha256 = hashlib.sha256(jpeg_bytes).hexdigest()

    # Re-open PIL Image from JPEG bytes for SDK submission
    sdk_image = Image.open(io.BytesIO(jpeg_bytes))
    return jpeg_bytes, image_sha256, sdk_image


class CatalogExtractor(CatalogExtractorProtocol):
    """Resilient 3-tier catalog attribute extractor for fashion apparel."""

    def __init__(
        self,
        adapter: GeminiAdapter | None = None,
        cache: CatalogCache | None = None,
        fixtures_dir: Path | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.adapter = adapter if adapter is not None else GeminiAdapter(settings=settings)
        self.cache = cache if cache is not None else get_catalog_cache()
        self.fixtures_dir = fixtures_dir if fixtures_dir is not None else FIXTURES_DIR

    def load_fixture(self, sku_id: str) -> ExtractedCatalogAttributes:
        """Load verified benchmark fixture from disk (Tier 3 fallback)."""
        normalized_id = sku_id.strip().lower().replace("-", "_")
        fixture_path = self.fixtures_dir / f"{normalized_id}.json"

        if fixture_path.exists():
            try:
                data = json.loads(fixture_path.read_text(encoding="utf-8"))
                attributes = ExtractedCatalogAttributes.model_validate(data)
                attributes.provenance = ProvenanceEnum.FIXTURE.value
                attributes.extracted_at = datetime.now(UTC)
                attributes.prompt_version = PROMPT_VERSION
                logger.info("[TIER 3 FIXTURE] Loaded verified benchmark for %s", sku_id)
                return attributes
            except Exception as exc:
                logger.warning(
                    "[TIER 3 ERROR] Failed loading fixture %s: %s. Using safe default.",
                    fixture_path,
                    exc,
                )

        # Fallback to curated dictionary if file missing
        curated_info = CURATED_SKUS.get(sku_id.upper())
        measurements: list[GarmentMeasurements] = []
        if curated_info and "sizes" in curated_info:
            for size_label, dim in curated_info["sizes"].items():
                measurements.append(
                    GarmentMeasurements(
                        size_label=size_label,
                        chest_inches=dim.get("chest"),
                        waist_inches=dim.get("waist"),
                        hip_inches=dim.get("hip"),
                        shoulder_inches=dim.get("shoulder"),
                        length_inches=dim.get("length"),
                    )
                )

        return ExtractedCatalogAttributes(
            garment_type=curated_info.get("name", "Fashion Apparel")
            if curated_info
            else "Standard Garment",
            silhouette="regular_straight",
            stretch_category=curated_info.get("fabric_stretch", "unknown")
            if curated_info
            else "unknown",
            stated_fabric="Cotton Blend",
            visible_closure="Standard Placket",
            measurements_table=measurements,
            missing_critical_data=["sleeve_length"] if sku_id.upper() == "SKU-03" else [],
            drape_notes=(
                "Standard garment structure. "
                "[Note: Sleeve length not specified by merchant; sizing calibrated via chest & shoulder circumference]"
                if sku_id.upper() == "SKU-03"
                else "Standard straight garment cut with balanced drape."
            ),
            provenance=ProvenanceEnum.FIXTURE.value,
            extracted_at=datetime.now(UTC),
            prompt_version=PROMPT_VERSION,
        )

    async def extract(
        self,
        sku_id: str,
        listing_text: str = "",
        image_bytes: bytes | None = None,
        image_path: str | None = None,
        force_refresh: bool = False,
    ) -> ExtractedCatalogAttributes:
        """Execute 3-tier extraction: Cache -> Live Gemini -> Verified Fixture."""
        norm_sku = sku_id.strip().upper()
        effective_text = (
            listing_text.strip()
            if listing_text.strip()
            else DEFAULT_LISTING_TEXTS.get(norm_sku, f"Garment listing for {norm_sku}")
        )

        # Preprocess image if provided
        processed_image: Image.Image | None = None
        image_sha256: str | None = None

        if image_bytes:
            _, image_sha256, processed_image = preprocess_image(image_bytes)
        elif image_path and Path(image_path).exists():
            _, image_sha256, processed_image = preprocess_image(Path(image_path))

        # Compute deterministic cache key
        cache_key = self.cache.compute_cache_key(
            norm_sku,
            image_sha256,
            self.adapter.model_id,
            PROMPT_VERSION,
        )

        # Tier 1: Check In-Memory TTL Cache
        if not force_refresh:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                cached_result.provenance = ProvenanceEnum.CACHE.value
                logger.info("[TIER 1 CACHE HIT] SKU %s (key=%s)", norm_sku, cache_key[:12])
                return cached_result

        # Tier 2: Live Gemini VLM Call
        try:
            contents: list[Any] = [build_catalog_prompt(norm_sku, effective_text)]
            if processed_image is not None:
                contents.append(processed_image)

            raw_text, tier_used = await self.adapter.generate_content(
                contents=contents,
                system_instruction=CATALOG_EXTRACTION_SYSTEM_PROMPT,
                response_schema=GeminiCatalogExtractionPayload,
                temperature=0.1,
            )

            # Validate structured output using tightened garment schema
            try:
                parsed_payload = GeminiCatalogExtractionPayload.model_validate_json(raw_text)
            except (ValidationError, ValueError, json.JSONDecodeError) as parse_err:
                logger.warning(
                    "[TIER 2 PARSE RETRY] Invalid JSON from %s (%s). Attempting repair.",
                    norm_sku,
                    parse_err,
                )
                # One repair retry
                repair_contents = [
                    CATALOG_REPAIR_SYSTEM_PROMPT,
                    f"Malformed output:\n{raw_text}",
                ]
                repaired_text, _ = await self.adapter.generate_content(
                    contents=repair_contents,
                    system_instruction=CATALOG_REPAIR_SYSTEM_PROMPT,
                    response_schema=GeminiCatalogExtractionPayload,
                    temperature=0.1,
                )
                parsed_payload = GeminiCatalogExtractionPayload.model_validate_json(repaired_text)

            # Construct server-authoritative attributes with provenance metadata
            result = ExtractedCatalogAttributes(
                **parsed_payload.model_dump(),
                provenance=ProvenanceEnum.LIVE_GEMINI.value,
                extracted_at=datetime.now(UTC),
                prompt_version=PROMPT_VERSION,
            )

            # Store in cache
            self.cache.set(cache_key, result)
            logger.info(
                "[TIER 2 LIVE SUCCESS] SKU %s extracted via %s (%s)",
                norm_sku,
                self.adapter.model_id,
                tier_used,
            )
            return result

        except (CircuitBreakerOpenException, GeminiAPIException, Exception) as exc:
            logger.warning(
                "[TIER 2 FAILED] SKU %s: %s (%s). Triggering Tier 3 fixture fallback.",
                norm_sku,
                type(exc).__name__,
                exc,
            )

        # Tier 3: Verified Benchmark Fixture Fallback
        fixture_result = self.load_fixture(norm_sku)
        # Store in cache so subsequent offline queries don't re-read disk
        self.cache.set(cache_key, fixture_result)
        return fixture_result
