"""Репозиторий: агрегированная статистика по аэропорту из PostgreSQL."""
from datetime import datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Airport, Flight


class StatsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def airport_exists(self, airport_code: str) -> bool:
        stmt = select(Airport.airport_code).where(Airport.airport_code == airport_code)
        row = (await self.session.execute(stmt)).first()
        return row is not None

    async def get_date_bounds(self) -> tuple[datetime, datetime]:
        stmt = select(func.min(Flight.scheduled_departure), func.max(Flight.scheduled_departure))
        lo, hi = (await self.session.execute(stmt)).one()
        return lo, hi

    async def get_stats(self, airport_code: str, date_from: datetime, date_to: datetime) -> Row:
        delay_minutes_expr = (
            func.extract("epoch", Flight.actual_departure - Flight.scheduled_departure) / 60.0
        )

        stmt = select(
            func.count().filter(Flight.departure_airport == airport_code).label("departures_count"),
            func.count().filter(Flight.arrival_airport == airport_code).label("arrivals_count"),
            func.count()
            .filter(and_(Flight.departure_airport == airport_code, Flight.status == "Delayed"))
            .label("delayed_count"),
            func.count()
            .filter(and_(Flight.departure_airport == airport_code, Flight.status == "Cancelled"))
            .label("cancelled_count"),
            func.avg(delay_minutes_expr)
            .filter(
                and_(
                    Flight.departure_airport == airport_code,
                    Flight.actual_departure.is_not(None),
                    Flight.actual_departure > Flight.scheduled_departure,
                )
            )
            .label("avg_delay_minutes"),
        ).where(
            or_(Flight.departure_airport == airport_code, Flight.arrival_airport == airport_code),
            Flight.scheduled_departure.between(date_from, date_to),
        )
        return (await self.session.execute(stmt)).one()

    async def get_popular_destinations(
        self, airport_code: str, date_from: datetime, date_to: datetime, top_n: int
    ) -> list[Row]:
        stmt = (
            select(
                Flight.arrival_airport.label("airport_code"),
                Airport.airport_name,
                func.count().label("flights_count"),
            )
            .join(Airport, Airport.airport_code == Flight.arrival_airport)
            .where(
                Flight.departure_airport == airport_code,
                Flight.scheduled_departure.between(date_from, date_to),
            )
            .group_by(Flight.arrival_airport, Airport.airport_name)
            .order_by(func.count().desc())
            .limit(top_n)
        )
        return (await self.session.execute(stmt)).all()
