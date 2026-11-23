"""Catalog API Endpoints for ReturnZero AI.

Provides product catalog retrieval routes per ADR-006, ADR-007, and AGENTS.md §7.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.api_contracts import SkuListResponse, SkuResponse
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get(
    "/skus",
    response_model=SkuListResponse,
    summary="List all catalog SKUs",
    description="Retrieve the 4 curated fashion SKUs with garment attributes and extraction provenance.",
    tags=["Catalog"],
)
async def list_skus(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SkuListResponse:
    """Retrieve full catalog listing."""
    service = CatalogService(session)
    return await service.list_skus()


@router.get(
    "/skus/{sku_id}",
    response_model=SkuResponse,
    summary="Get single SKU details",
    description="Retrieve complete garment specifications, size table, and provenance for a given SKU ID.",
    tags=["Catalog"],
)
async def get_sku(
    sku_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SkuResponse:
    """Retrieve single SKU by ID or 404."""
    service = CatalogService(session)
    sku = await service.get_sku(sku_id)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU '{sku_id}' not found in catalog",
        )
    return sku
