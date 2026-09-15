"""Роутер: HTTP-эндпойнты статистики по аэропорту."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas import AirportStatsOut
from app.services.stats_service import StatsService

router = APIRouter(prefix="/api/v1/stats/airports", tags=["stats"])


@router.get("/{airport_code}", response_model=AirportStatsOut)
async def get_airport_stats(
    airport_code: str = Path(..., min_length=3, max_length=3),
    date_from: datetime | None = Query(None, description="Начало периода. По умолчанию — вся история"),
    date_to: datetime | None = Query(None, description="Конец периода. По умолчанию — вся история"),
    top_n: int = Query(5, ge=1, le=20, description="Сколько популярных направлений вернуть"),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await StatsService(db).get_airport_stats(airport_code, date_from, date_to, top_n)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
