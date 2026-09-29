"""Liveness and readiness. Canonical example for new endpoints: thin handler, Depends() wiring, problem details."""

import asyncio
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from capsule_core.api.deps import get_session, get_settings
from capsule_core.errors import PROBLEM_BASE, problem
from capsule_core.settings import Settings

router = APIRouter(tags=["health"])
log = structlog.get_logger(__name__)


@router.get("/healthz")
async def healthz(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, str]:
    """Process is up. Never touches the database."""
    return {"status": "ok", "version": settings.service_version}


@router.get("/readyz", response_model=None)
async def readyz(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str] | JSONResponse:
    """Ready to serve: Postgres answers `SELECT 1` within READYZ_TIMEOUT_S."""
    try:
        async with asyncio.timeout(settings.readyz_timeout_s):
            await session.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError, TimeoutError) as exc:
        log.warning("readyz.db_unavailable", error_type=type(exc).__name__)
        return problem(
            503,
            instance=request.url.path,
            type_=PROBLEM_BASE + "dependency-unavailable",
            detail="Database unavailable.",
        )
    return {"status": "ok"}
