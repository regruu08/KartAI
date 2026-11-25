"""Demo State Management API Endpoints for ReturnZero AI.

Provides guarded administrative reset endpoint restoring the database to the pristine
150-order seed state on demand per ADR-009 and AGENTS.md §7.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.config import Settings, get_settings
from app.db.seed import seed_initial_data
from app.db.session import get_db_session, reset_db
from app.schemas.api_contracts import DemoResetResponse

router = APIRouter()


@router.post(
    "/reset",
    response_model=DemoResetResponse,
    summary="Reset Demo Database State",
    description="Wipes and restores the database to the pristine 150-order deterministic seed state.",
    tags=["Demo"],
)
async def reset_demo_state(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    x_demo_token: Annotated[str | None, Header(alias="X-Demo-Token")] = None,
) -> DemoResetResponse:
    """Reset database to initial pristine state if authorized."""
    if not settings.DEMO_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo reset endpoint is disabled outside of demo mode.",
        )

    expected_token = settings.DEMO_TOKEN.get_secret_value()
    if not x_demo_token or x_demo_token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Demo-Token header.",
        )

    # Reset database schema on the app-bound engine and re-seed 150 historical records
    app_engine: AsyncEngine | None = getattr(request.app.state, "engine", None)
    await reset_db(engine_override=app_engine)
    seed_result = await seed_initial_data(session)
    await session.commit()

    return DemoResetResponse(
        status="ok",
        message="Database reset to pristine 150-order seed state",
        seeded_orders=seed_result["orders"],
        seeded_skus=seed_result["skus"],
    )
