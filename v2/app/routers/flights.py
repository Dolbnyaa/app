"""Роутер: HTTP-эндпойнты для рейсов."""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas import FlightDetailOut, FlightListOut
from app.services.flight_service import FlightService

router = APIRouter(prefix="/api/v1/flights", tags=["flights"])

Lang = Literal["en", "ru"]


@router.get("", response_model=FlightListOut)
async def list_flights(
    departure_airport: str | None = Query(None, min_length=3, max_length=3),
    arrival_airport: str | None = Query(None, min_length=3, max_length=3),
    status: str | None = Query(
        None, description="On Time / Delayed / Departed / Arrived / Scheduled / Cancelled"
    ),
    date_from: datetime | None = Query(None, description="Фильтр по scheduled_departure, включительно"),
    date_to: datetime | None = Query(None, description="Фильтр по scheduled_departure, включительно"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await FlightService(db).list_flights(
        departure_airport, arrival_airport, status, date_from, date_to, limit, offset
    )


@router.get("/{flight_id}", response_model=FlightDetailOut)
async def get_flight(
    flight_id: int,
    lang: Lang = Query(settings.default_lang),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await FlightService(db).get_flight(flight_id, lang)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
