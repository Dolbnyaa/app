"""Сервис: прикладная логика для рейсов."""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.flight_repository import FlightRepository
from app.schemas import AircraftBrief, AirportBrief, FlightDetailOut, FlightListItem, FlightListOut
from app.services.common import jsonb_lang


class FlightService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = FlightRepository(session)

    async def list_flights(
        self,
        departure_airport: str | None,
        arrival_airport: str | None,
        status: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        limit: int,
        offset: int,
    ) -> FlightListOut:
        departure_airport = departure_airport.upper() if departure_airport else None
        arrival_airport = arrival_airport.upper() if arrival_airport else None

        total = await self.repo.count_filtered(
            departure_airport, arrival_airport, status, date_from, date_to
        )
        rows = await self.repo.list_filtered(
            departure_airport, arrival_airport, status, date_from, date_to, limit, offset
        )

        items = [
            FlightListItem(
                flight_id=f.flight_id,
                flight_no=f.flight_no.strip(),
                scheduled_departure=f.scheduled_departure,
                scheduled_arrival=f.scheduled_arrival,
                departure_airport=f.departure_airport.strip(),
                arrival_airport=f.arrival_airport.strip(),
                status=f.status,
                aircraft_code=f.aircraft_code.strip(),
            )
            for f in rows
        ]
        return FlightListOut(total=total, limit=limit, offset=offset, items=items)

    async def get_flight(self, flight_id: int, lang: str) -> FlightDetailOut:
        flight = await self.repo.get_by_id(flight_id)
        if flight is None:
            raise NotFoundError(f"Рейс с id={flight_id} не найден")

        dep = flight.departure_airport_obj
        arr = flight.arrival_airport_obj
        ac = flight.aircraft

        return FlightDetailOut(
            flight_id=flight.flight_id,
            flight_no=flight.flight_no.strip(),
            status=flight.status,
            departure_airport=AirportBrief(
                airport_code=dep.airport_code.strip(),
                airport_name=jsonb_lang(dep.airport_name, lang),
                city=jsonb_lang(dep.city, lang),
            ),
            arrival_airport=AirportBrief(
                airport_code=arr.airport_code.strip(),
                airport_name=jsonb_lang(arr.airport_name, lang),
                city=jsonb_lang(arr.city, lang),
            ),
            aircraft=AircraftBrief(
                aircraft_code=ac.aircraft_code.strip(),
                model=jsonb_lang(ac.model, lang),
                range=ac.range,
            ),
            scheduled_departure=flight.scheduled_departure,
            scheduled_arrival=flight.scheduled_arrival,
            actual_departure=flight.actual_departure,
            actual_arrival=flight.actual_arrival,
        )
