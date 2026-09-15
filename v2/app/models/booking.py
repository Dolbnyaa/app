"""ORM-модель бронирования (bookings.bookings)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = {"schema": "bookings"}

    book_ref: Mapped[str] = mapped_column(String(6), primary_key=True)
    book_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
