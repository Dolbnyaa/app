"""Роутер: HTTP-эндпойнты для рейсов пассажира."""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas import PassengerFlightItem
from app.services.passenger_service import PassengerService

router = APIRouter(prefix="/api/v1/passengers", tags=["passengers"])


@router.get("/{passenger_id}/flights", response_model=list[PassengerFlightItem])
async def get_passenger_flights(
    passenger_id: str = Path(..., description="Номер документа пассажира, напр. '4098 174300'"),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await PassengerService(db).get_passenger_flights(passenger_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
