"""Собирает все Pydantic-схемы в одном месте: `from app.schemas import AirportOut, ...`."""
from app.schemas.airport import AirportOut
from app.schemas.flight import (
    AircraftBrief,
    AirportBrief,
    FlightDetailOut,
    FlightListItem,
    FlightListOut,
)
from app.schemas.health import HealthOut
from app.schemas.passenger import PassengerFlightItem
from app.schemas.stats import AirportStatsOut, PopularDestination

__all__ = [
    "AircraftBrief",
    "AirportBrief",
    "AirportOut",
    "AirportStatsOut",
    "FlightDetailOut",
    "FlightListItem",
    "FlightListOut",
    "HealthOut",
    "PassengerFlightItem",
    "PopularDestination",
]
