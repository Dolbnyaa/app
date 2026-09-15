"""Сервис: прикладная логика для рейсов конкретного пассажира."""
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.passenger_repository import PassengerRepository
from app.schemas import PassengerFlightItem


class PassengerService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = PassengerRepository(session)

    async def get_passenger_flights(self, passenger_id: str) -> list[PassengerFlightItem]:
        rows = await self.repo.get_flights(passenger_id)
        if not rows:
            raise NotFoundError(
                f"Пассажир с номером документа '{passenger_id}' не найден или у него нет рейсов"
            )

        return [
            PassengerFlightItem(
                ticket_no=ticket.ticket_no.strip(),
                book_ref=ticket.book_ref.strip(),
                flight_id=flight.flight_id,
                flight_no=flight.flight_no.strip(),
                departure_airport=flight.departure_airport.strip(),
                arrival_airport=flight.arrival_airport.strip(),
                scheduled_departure=flight.scheduled_departure,
                scheduled_arrival=flight.scheduled_arrival,
                status=flight.status,
                fare_conditions=tf.fare_conditions,
                amount=Decimal(tf.amount),
                seat_no=boarding.seat_no.strip() if boarding else None,
            )
            for ticket, tf, flight, boarding in rows
        ]
