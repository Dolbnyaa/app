"""
Aviation Demo API — многослойная версия
=========================================
REST API поверх демо-базы postgrespro (авиаперевозки, схема `bookings`).

Слои приложения:
    core         — настройки и кастомные исключения приложения
    db           — engine, фабрика сессий, базовый класс ORM-моделей
    models       — SQLAlchemy ORM-модели (таблицы)
    schemas      — Pydantic-модели запросов/ответов
    repositories — запросы к PostgreSQL, ничего не знают про HTTP
    services     — прикладная логика, превращает ORM-объекты в схемы
    routers      — HTTP-эндпойнты, тонкий слой поверх сервисов

Запуск:
    uvicorn app.main:app --reload

Документация (Swagger UI) после запуска: http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import connect_engine, disconnect_engine
from app.routers import airports, flights, health, passengers, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_engine()
    yield
    await disconnect_engine()


app = FastAPI(
    title="Aviation Demo API",
    description=(
        "REST API поверх демо-базы данных авиаперевозок postgrespro "
        "(SQLAlchemy, слоистая архитектура)"
    ),
    version="3.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(airports.router)
app.include_router(flights.router)
app.include_router(passengers.router)
app.include_router(stats.router)
