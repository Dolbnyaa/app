"""Pydantic-модели, описывающие форму JSON-ответов API."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ---------- /api/v1/airports ----------

class AirportOut(BaseModel):
    airport_code: str = Field(..., description="Трёхбуквенный код IATA")
    airport_name: str
    city: str
    longitude: float
    latitude: float
    timezone: str


# ---------- /api/v1/flights ----------

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


# ---------- /api/v1/passengers/{passenger_id}/flights ----------

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


# ---------- /api/v1/stats/airports/{airport_code} ----------

class PopularDestination(BaseModel):
    airport_code: str
    airport_name: str
    flights_count: int


class AirportStatsOut(BaseModel):
    airport_code: str
    period_from: datetime
    period_to: datetime
    departures_count: int
    arrivals_count: int
    delayed_count: int
    cancelled_count: int
    avg_delay_minutes: float | None
    popular_destinations: list[PopularDestination]


# ---------- /health ----------

class HealthOut(BaseModel):
    status: str
    database: str
