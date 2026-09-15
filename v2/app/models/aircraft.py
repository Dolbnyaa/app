"""ORM-модель самолёта (bookings.aircrafts_data)."""
from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Aircraft(Base):
    __tablename__ = "aircrafts_data"
    __table_args__ = {"schema": "bookings"}

    aircraft_code: Mapped[str] = mapped_column(String(3), primary_key=True)
    model: Mapped[dict] = mapped_column(JSONB)
    range: Mapped[int] = mapped_column(Integer)
