"""Pydantic-схемы ответа для /api/v1/stats/airports/{airport_code}."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


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
