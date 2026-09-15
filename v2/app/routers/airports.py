"""Роутер: HTTP-эндпойнты для аэропортов."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas import AirportOut
from app.services.airport_service import AirportService

router = APIRouter(prefix="/api/v1/airports", tags=["airports"])

Lang = Literal["en", "ru"]


@router.get("", response_model=list[AirportOut])
async def list_airports(
    lang: Lang = Query(settings.default_lang, description="Язык названия: en/ru"),
    db: AsyncSession = Depends(get_db),
):
    return await AirportService(db).list_airports(lang)


@router.get("/{airport_code}", response_model=AirportOut)
async def get_airport(
    airport_code: str = Path(..., min_length=3, max_length=3, description="Код IATA, напр. SVO"),
    lang: Lang = Query(settings.default_lang),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await AirportService(db).get_airport(airport_code, lang)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
