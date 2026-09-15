"""Pydantic-схемы ответов для /api/v1/flights."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FlightListItem(BaseModel):
    flight_id: int
    flight_no: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    departure_airport: str
    arrival_airport: str
    status: str
    aircraft_code: str


class FlightListOut(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[FlightListItem]


class AirportBrief(BaseModel):
    airport_code: str
    airport_name: str
    city: str


class AircraftBrief(BaseModel):
    aircraft_code: str
    model: str
    range: int


class FlightDetailOut(BaseModel):
    flight_id: int
    flight_no: str
    status: str
    departure_airport: AirportBrief
    arrival_airport: AirportBrief
    aircraft: AircraftBrief
    scheduled_departure: datetime
    scheduled_arrival: datetime
    actual_departure: datetime | None
    actual_arrival: datetime | None
