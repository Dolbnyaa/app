"""Репозиторий: получение данных о рейсах из PostgreSQL."""
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Flight


class FlightRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _build_conditions(
        departure_airport: str | None,
        arrival_airport: str | None,
        status: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list:
        conditions = []
        if departure_airport:
            conditions.append(Flight.departure_airport == departure_airport)
        if arrival_airport:
            conditions.append(Flight.arrival_airport == arrival_airport)
        if status:
            conditions.append(Flight.status == status)
        if date_from:
            conditions.append(Flight.scheduled_departure >= date_from)
        if date_to:
            conditions.append(Flight.scheduled_departure <= date_to)
        return conditions

    async def count_filtered(
        self,
        departure_airport: str | None,
        arrival_airport: str | None,
        status: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> int:
        conditions = self._build_conditions(
            departure_airport, arrival_airport, status, date_from, date_to
        )
        stmt = select(func.count()).select_from(Flight)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        return (await self.session.execute(stmt)).scalar_one()

    async def list_filtered(
        self,
        departure_airport: str | None,
        arrival_airport: str | None,
        status: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        limit: int,
        offset: int,
    ) -> Sequence[Flight]:
        conditions = self._build_conditions(
            departure_airport, arrival_airport, status, date_from, date_to
        )
        stmt = select(Flight)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Flight.scheduled_departure).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, flight_id: int) -> Flight | None:
        stmt = (
            select(Flight)
            .options(
                joinedload(Flight.departure_airport_obj),
                joinedload(Flight.arrival_airport_obj),
                joinedload(Flight.aircraft),
            )
            .where(Flight.flight_id == flight_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_date_bounds(self) -> tuple[datetime, datetime]:
        stmt = select(func.min(Flight.scheduled_departure), func.max(Flight.scheduled_departure))
        lo, hi = (await self.session.execute(stmt)).one()
        return lo, hi
