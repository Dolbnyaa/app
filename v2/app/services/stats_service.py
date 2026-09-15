"""Сервис: прикладная логика статистики по аэропорту."""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.stats_repository import StatsRepository
from app.schemas import AirportStatsOut, PopularDestination
from app.services.common import jsonb_lang


class StatsService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = StatsRepository(session)

    async def get_airport_stats(
        self,
        airport_code: str,
        date_from: datetime | None,
        date_to: datetime | None,
        top_n: int,
    ) -> AirportStatsOut:
        code = airport_code.upper()

        if not await self.repo.airport_exists(code):
            raise NotFoundError(f"Аэропорт '{airport_code}' не найден")

        if date_from is None or date_to is None:
            lo, hi = await self.repo.get_date_bounds()
            date_from = date_from or lo
            date_to = date_to or hi

        stats_row = await self.repo.get_stats(code, date_from, date_to)
        popular_rows = await self.repo.get_popular_destinations(code, date_from, date_to, top_n)

        return AirportStatsOut(
            airport_code=code,
            period_from=date_from,
            period_to=date_to,
            departures_count=stats_row.departures_count,
            arrivals_count=stats_row.arrivals_count,
            delayed_count=stats_row.delayed_count,
            cancelled_count=stats_row.cancelled_count,
            avg_delay_minutes=(
                round(stats_row.avg_delay_minutes, 1)
                if stats_row.avg_delay_minutes is not None
                else None
            ),
            popular_destinations=[
                PopularDestination(
                    airport_code=row.airport_code.strip(),
                    airport_name=jsonb_lang(row.airport_name, "en"),
                    flights_count=row.flights_count,
                )
                for row in popular_rows
            ],
        )
