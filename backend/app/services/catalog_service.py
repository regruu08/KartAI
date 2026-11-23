"""Catalog Service for ReturnZero AI.

Coordinates product catalog retrieval, attribute synchronization, and SKU data
persistence per ADR-006 and AGENTS.md §7.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SkuModel
from app.db.repositories import SkuRepository
from app.integrations.gemini.extractor import CatalogExtractor
from app.schemas.api_contracts import (
    ExtractCatalogRequest,
    SkuListResponse,
    SkuResponse,
)


class CatalogService:
    """Service handling product catalog queries and schema conversion."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = SkuRepository(session)

    @staticmethod
    def to_sku_response(model: SkuModel) -> SkuResponse:
        """Convert an SKU database model to an API response contract."""
        return SkuResponse(
            id=model.id,
            name=model.name,
            category=model.category,
            price_inr=model.price_inr,
            fabric_composition=model.fabric_composition,
            fabric_stretch=model.fabric_stretch,
            has_shoulder=model.has_shoulder,
            has_sleeve=model.has_sleeve,
            length_inches=model.length_inches,
            sizes_json=model.sizes_json,
            care_instructions=model.care_instructions,
            provenance=model.provenance,
            extracted_at=model.extracted_at,
            prompt_version=model.prompt_version,
            image_sha256=model.image_sha256,
        )

    async def get_sku(self, sku_id: str) -> SkuResponse | None:
        """Retrieve an SKU by its unique ID."""
        model = await self.repo.get_by_id(sku_id)
        if not model:
            return None
        return self.to_sku_response(model)

    async def list_skus(self) -> SkuListResponse:
        """List all catalog SKUs."""
        models: Sequence[SkuModel] = await self.repo.list_all()
        sku_responses = [self.to_sku_response(m) for m in models]
        return SkuListResponse(skus=sku_responses, total=len(sku_responses))

    async def extract_and_update(
        self,
        sku_id: str,
        request: ExtractCatalogRequest | None = None,
        extractor: CatalogExtractor | None = None,
    ) -> SkuResponse | None:
        """Run multimodal extraction for an SKU and persist updated attributes."""
        model = await self.repo.get_by_id(sku_id)
        if not model:
            return None

        active_extractor = extractor or CatalogExtractor()
        listing_text = (
            request.listing_text
            if request and request.listing_text
            else f"{model.name}. {model.fabric_composition}."
        )
        image_path = request.image_path if request else None
        force_refresh = request.force_refresh if request else False

        extracted = await active_extractor.extract(
            sku_id=sku_id,
            listing_text=listing_text,
            image_path=image_path,
            force_refresh=force_refresh,
        )

        # Synchronize extracted attributes into DB model (ADR-006)
        model.provenance = extracted.provenance
        model.extracted_at = extracted.extracted_at or datetime.now(UTC)
        model.prompt_version = extracted.prompt_version

        if extracted.stated_fabric:
            model.fabric_composition = extracted.stated_fabric
        if extracted.stretch_category != "unknown":
            model.fabric_stretch = extracted.stretch_category

        if extracted.measurements_table:
            sizes_dict: dict[str, Any] = {}
            for m in extracted.measurements_table:
                sizes_dict[m.size_label] = {
                    k: v
                    for k, v in {
                        "chest": m.chest_inches,
                        "waist": m.waist_inches,
                        "hip": m.hip_inches,
                        "shoulder": m.shoulder_inches,
                        "length": m.length_inches,
                    }.items()
                    if v is not None
                }
            if sizes_dict:
                model.sizes_json = sizes_dict

        if "sleeve_length" in extracted.missing_critical_data:
            model.has_sleeve = False

        await self.repo.upsert(model)
        await self.session.commit()
        return self.to_sku_response(model)
