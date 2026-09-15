"""Репозиторий: получение рейсов конкретного пассажира из PostgreSQL."""
from sqlalchemy import and_, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models import BoardingPass, Flight, Ticket, TicketFlight


class PassengerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_flights(self, passenger_id: str) -> list[Row]:
        # bp — псевдоним BoardingPass, аналог "AS bp" в обычном SQL:
        # нужен для явного LEFT JOIN по составному условию.
        bp = aliased(BoardingPass)
        stmt = (
            select(Ticket, TicketFlight, Flight, bp)
            .join(TicketFlight, TicketFlight.ticket_no == Ticket.ticket_no)
            .join(Flight, Flight.flight_id == TicketFlight.flight_id)
            .outerjoin(
                bp,
                and_(bp.ticket_no == TicketFlight.ticket_no, bp.flight_id == TicketFlight.flight_id),
            )
            .where(Ticket.passenger_id == passenger_id)
            .order_by(Flight.scheduled_departure)
        )
        return (await self.session.execute(stmt)).all()
