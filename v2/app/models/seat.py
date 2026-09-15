"""ORM-модель места в самолёте (bookings.seats)."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = {"schema": "bookings"}

    aircraft_code: Mapped[str] = mapped_column(
        String(3), ForeignKey("bookings.aircrafts_data.aircraft_code"), primary_key=True
    )
    seat_no: Mapped[str] = mapped_column(String(4), primary_key=True)
    fare_conditions: Mapped[str] = mapped_column(String(10))
