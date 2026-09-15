"""Pydantic-схема ответа /health."""
from pydantic import BaseModel


class HealthOut(BaseModel):
    status: str
    database: str
