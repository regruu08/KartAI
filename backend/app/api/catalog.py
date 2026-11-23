"""Catalog API Endpoints for ReturnZero AI.

Provides product catalog retrieval routes per ADR-006, ADR-007, and AGENTS.md §7.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domain.sizing import recommend_size
from app.schemas.api_contracts import (
    ExtractCatalogRequest,
    FitRecommendationResponse,
    FitRecommendRequest,
    SkuListResponse,
    SkuResponse,
)
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


@router.post(
    "/skus/{sku_id}/extract",
    response_model=SkuResponse,
    summary="Extract SKU attributes via multimodal VLM",
    description="Run 3-tier extraction flow (cache -> live Gemini -> fixture), persist attributes, and return updated SKU.",
    tags=["Catalog"],
)
async def extract_sku(
    sku_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: ExtractCatalogRequest | None = None,
) -> SkuResponse:
    """Run multimodal extraction for a given SKU and synchronize database state."""
    service = CatalogService(session)
    sku = await service.extract_and_update(sku_id, request)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU '{sku_id}' not found in catalog",
        )
    return sku


@router.post(
    "/skus/{sku_id}/fit",
    response_model=FitRecommendationResponse,
    summary="Compute deterministic size recommendation",
    description="Calculates recommended size, confidence band, and fit zone breakdown using pure domain EOM rules.",
    tags=["Catalog"],
)
async def compute_sku_fit(
    sku_id: str,
    request: FitRecommendRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FitRecommendationResponse:
    """Calculate sizing recommendation against SKU measurements."""
    service = CatalogService(session)
    sku = await service.get_sku(sku_id)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU '{sku_id}' not found in catalog",
        )
    recommendation = recommend_size(
        sku_id=sku_id,
        known_brand=request.known_brand,
        known_size=request.known_size,
        fit_preference=request.fit_preference,
        height_cm=request.height_cm,
        chest_inches=request.chest_inches,
        waist_inches=request.waist_inches,
    )
    return FitRecommendationResponse(
        sku_id=recommendation.sku_id,
        recommended_size=recommendation.recommended_size,
        confidence_level=recommendation.confidence_level,
        fit_score=recommendation.fit_score,
        fit_zone_breakdown=recommendation.fit_zone_breakdown,
        explanation_text=recommendation.explanation_text,
        missing_data_warnings=recommendation.missing_data_warnings,
    )
