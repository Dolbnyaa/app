"""ORM-модель посадочного талона (bookings.boarding_passes)."""
from __future__ import annotations

from sqlalchemy import ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BoardingPass(Base):
    __tablename__ = "boarding_passes"

    ticket_no: Mapped[str] = mapped_column(String(13), primary_key=True)
    flight_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    boarding_no: Mapped[int] = mapped_column(Integer)
    seat_no: Mapped[str] = mapped_column(String(4))

    # Составной внешний ключ (ticket_no, flight_id) -> ticket_flights,
    # поэтому обычного ForeignKey() на одной колонке недостаточно —
    # нужен ForeignKeyConstraint на уровне таблицы целиком.
    __table_args__ = (
        ForeignKeyConstraint(
            ["ticket_no", "flight_id"],
            ["bookings.ticket_flights.ticket_no", "bookings.ticket_flights.flight_id"],
        ),
        {"schema": "bookings"},
    )
