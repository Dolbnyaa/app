"""Pydantic-схемы ответов для /api/v1/airports."""
from pydantic import BaseModel, Field


class AirportOut(BaseModel):
    airport_code: str = Field(..., description="Трёхбуквенный код IATA")
    airport_name: str
    city: str
    longitude: float
    latitude: float
    timezone: str
