"""ORM-модель рейса (bookings.flights)."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.aircraft import Aircraft
    from app.models.airport import Airport


class Flight(Base):
    __tablename__ = "flights"
    __table_args__ = {"schema": "bookings"}

    flight_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    flight_no: Mapped[str] = mapped_column(String(6))
    scheduled_departure: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scheduled_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    departure_airport: Mapped[str] = mapped_column(
        String(3), ForeignKey("bookings.airports_data.airport_code")
    )
    arrival_airport: Mapped[str] = mapped_column(
        String(3), ForeignKey("bookings.airports_data.airport_code")
    )
    status: Mapped[str] = mapped_column(String(20))
    aircraft_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("bookings.aircrafts_data.aircraft_code")
    )
    actual_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # У flights ДВА внешних ключа на airports_data (вылет и прилёт),
    # поэтому для каждой relationship нужно явно указать foreign_keys —
    # иначе SQLAlchemy не поймёт, какую колонку использовать для связи.
    departure_airport_obj: Mapped["Airport"] = relationship(foreign_keys=[departure_airport])
    arrival_airport_obj: Mapped["Airport"] = relationship(foreign_keys=[arrival_airport])
    aircraft: Mapped["Aircraft"] = relationship()
