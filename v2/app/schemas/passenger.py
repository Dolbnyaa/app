"""Pydantic-схема ответа для /api/v1/passengers/{passenger_id}/flights."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PassengerFlightItem(BaseModel):
    ticket_no: str
    book_ref: str
    flight_id: int
    flight_no: str
    departure_airport: str
    arrival_airport: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    status: str
    fare_conditions: str
    amount: Decimal
    seat_no: str | None = Field(None, description="Место, если оформлен посадочный талон")
