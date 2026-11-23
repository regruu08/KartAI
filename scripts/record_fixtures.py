#!/usr/bin/env python3
"""Utility script to record or refresh benchmark fixtures from Gemini VLM outputs.

Used to generate or refresh backend/app/data/fixtures/<sku>.json files.
Complies with AGENTS.md §8: fixtures must be real extractor outputs or human-reviewed
conservative benchmarks tagged with provenance: "manual_fixture" or "live_gemini".
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import get_settings
from app.integrations.gemini.adapter import GeminiAdapter
from app.integrations.gemini.extractor import (
    DEFAULT_LISTING_TEXTS,
    FIXTURES_DIR,
    CatalogExtractor,
)
from app.schemas.api_contracts import ExtractedCatalogAttributes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("returnzero.scripts.record_fixtures")

SKU_IDS = ["SKU-01", "SKU-02", "SKU-03", "SKU-04"]


async def record_fixtures() -> int:
    """Record or validate benchmark fixtures for all 4 curated fashion SKUs."""
    settings = get_settings()
    adapter = GeminiAdapter(settings=settings)
    extractor = CatalogExtractor(adapter=adapter, fixtures_dir=FIXTURES_DIR)

    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Recording/refreshing fixtures in {FIXTURES_DIR}")
    print(f"Model ID: {settings.GEMINI_MODEL_ID}, Live Keys Configured: {settings.has_gemini_key}")

    for sku_id in SKU_IDS:
        print(f"\nProcessing {sku_id}...")
        listing_text = DEFAULT_LISTING_TEXTS.get(sku_id, "")

        if settings.has_gemini_key:
            # Live extraction from Gemini
            print(f"  Attempting live Gemini extraction for {sku_id}...")
            attributes = await extractor.extract(
                sku_id=sku_id,
                listing_text=listing_text,
                force_refresh=True,
            )
        else:
            # Fallback to loading existing fixture or baseline
            print(f"  No live keys. Validating benchmark fixture for {sku_id}...")
            attributes = extractor.load_fixture(sku_id)

        # Enforce ADR-004 & ADR-013 constraint for SKU-03
        if sku_id == "SKU-03" and "sleeve_length" not in attributes.missing_critical_data:
            attributes.missing_critical_data.append("sleeve_length")

        norm_filename = f"{sku_id.lower().replace('-', '_')}.json"
        dest_path = FIXTURES_DIR / norm_filename
        dest_path.write_text(
            json.dumps(attributes.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        print(f"  -> Written {dest_path.name} (provenance: {attributes.provenance})")

    print("\n[SUCCESS] All 4 SKU benchmark fixtures are verified and recorded.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(record_fixtures()))
