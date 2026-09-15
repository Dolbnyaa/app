"""ORM-модель билета (bookings.tickets)."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": "bookings"}

    ticket_no: Mapped[str] = mapped_column(String(13), primary_key=True)
    book_ref: Mapped[str] = mapped_column(String(6), ForeignKey("bookings.bookings.book_ref"))
    passenger_id: Mapped[str] = mapped_column(String(20))
    passenger_name: Mapped[str] = mapped_column(Text)
    contact_data: Mapped[dict | None] = mapped_column(JSONB)
