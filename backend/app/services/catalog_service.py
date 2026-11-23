"""Catalog Service for ReturnZero AI.

Coordinates product catalog retrieval, attribute synchronization, and SKU data
persistence per ADR-006 and AGENTS.md §7.
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SkuModel
from app.db.repositories import SkuRepository
from app.schemas.api_contracts import SkuListResponse, SkuResponse


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
