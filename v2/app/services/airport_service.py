"""Сервис: прикладная логика для аэропортов — превращает ORM-объекты в схемы ответа."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Airport
from app.repositories.airport_repository import AirportRepository
from app.schemas import AirportOut
from app.services.common import jsonb_lang


class AirportService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AirportRepository(session)

    async def list_airports(self, lang: str) -> list[AirportOut]:
        airports = await self.repo.list_all()
        return [self._to_schema(a, lang) for a in airports]

    async def get_airport(self, airport_code: str, lang: str) -> AirportOut:
        airport = await self.repo.get_by_code(airport_code.upper())
        if airport is None:
            raise NotFoundError(f"Аэропорт '{airport_code}' не найден")
        return self._to_schema(airport, lang)

    @staticmethod
    def _to_schema(airport: Airport, lang: str) -> AirportOut:
        return AirportOut(
            airport_code=airport.airport_code.strip(),
            airport_name=jsonb_lang(airport.airport_name, lang),
            city=jsonb_lang(airport.city, lang),
            longitude=airport.coordinates[0],
            latitude=airport.coordinates[1],
            timezone=airport.timezone,
        )
