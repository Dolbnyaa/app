"""ORM-модель связи билета и рейса (bookings.ticket_flights)."""
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.flight import Flight
    from app.models.ticket import Ticket


class TicketFlight(Base):
    __tablename__ = "ticket_flights"
    __table_args__ = {"schema": "bookings"}

    ticket_no: Mapped[str] = mapped_column(
        String(13), ForeignKey("bookings.tickets.ticket_no"), primary_key=True
    )
    flight_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bookings.flights.flight_id"), primary_key=True
    )
    fare_conditions: Mapped[str] = mapped_column(String(10))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    flight: Mapped["Flight"] = relationship()
    ticket: Mapped["Ticket"] = relationship()
