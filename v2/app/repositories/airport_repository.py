"""Репозиторий: получение данных об аэропортах из PostgreSQL."""
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Airport


class AirportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> Sequence[Airport]:
        stmt = select(Airport).order_by(Airport.airport_code)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_code(self, airport_code: str) -> Airport | None:
        stmt = select(Airport).where(Airport.airport_code == airport_code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
