"""ORM-модель аэропорта (bookings.airports_data)."""
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Point


class Airport(Base):
    __tablename__ = "airports_data"
    __table_args__ = {"schema": "bookings"}

    airport_code: Mapped[str] = mapped_column(String(3), primary_key=True)
    airport_name: Mapped[dict] = mapped_column(JSONB)
    city: Mapped[dict] = mapped_column(JSONB)
    coordinates: Mapped[tuple] = mapped_column(Point)
    timezone: Mapped[str] = mapped_column(Text)
