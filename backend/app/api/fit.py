"""Fit Intelligence API Endpoints for ReturnZero AI.

Provides canonical size recommendation route per AGENTS.md §7 and ADR-007.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FitLogModel
from app.db.session import get_db_session
from app.domain.sizing import recommend_size
from app.schemas.api_contracts import (
    FitRecommendationResponse,
    FitRecommendRequest,
)
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.post(
    "/recommend",
    response_model=FitRecommendationResponse,
    summary="Compute deterministic size recommendation and record audit log",
    description="Calculates recommended size and persists an auditable FitLogModel entry per AGENTS.md §7.",
    tags=["Fit"],
)
async def recommend_fit(
    request: FitRecommendRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FitRecommendationResponse:
    """Calculate sizing recommendation against SKU measurements and persist audit log."""
    sku_id = request.sku_id.strip()
    if not sku_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Field 'sku_id' is required in request body.",
        )

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
        custom_catalog=CatalogService.to_sizing_catalog(sku),
    )

    # Persist FitLogModel entry per AGENTS.md §7 contract
    fit_log = FitLogModel(
        id=f"fit_{uuid.uuid4().hex[:12]}",
        sku_id=sku_id,
        order_id=None,
        known_brand=request.known_brand,
        known_size=request.known_size,
        recommended_size=recommendation.recommended_size,
        confidence_level=recommendation.confidence_level,
        fit_score=recommendation.fit_score,
        is_correct=None,
    )
    session.add(fit_log)
    await session.commit()

    return FitRecommendationResponse(
        sku_id=recommendation.sku_id,
        recommended_size=recommendation.recommended_size,
        confidence_level=recommendation.confidence_level,
        fit_score=recommendation.fit_score,
        fit_zone_breakdown=recommendation.fit_zone_breakdown,
        explanation_text=recommendation.explanation_text,
        missing_data_warnings=recommendation.missing_data_warnings,
    )
