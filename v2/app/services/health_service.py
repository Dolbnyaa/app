"""Сервис: проверка работоспособности приложения и подключения к БД."""
from app.db.session import check_connection
from app.schemas import HealthOut


class HealthService:
    async def check(self) -> tuple[bool, HealthOut]:
        db_ok = await check_connection()
        payload = HealthOut(
            status="ok" if db_ok else "error",
            database="connected" if db_ok else "unavailable",
        )
        return db_ok, payload
