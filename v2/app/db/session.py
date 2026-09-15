"""
Асинхронный движок и фабрика сессий SQLAlchemy для PostgreSQL.

Пул соединений целиком под управлением SQLAlchemy (движок сам содержит
внутренний пул), а работа с БД идёт через объект `AsyncSession`.
Жизненным циклом движка управляет lifespan в app/main.py через
connect_engine()/disconnect_engine().
"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def connect_engine() -> None:
    global _engine, _session_factory
    _engine = create_async_engine(
        settings.sqlalchemy_dsn,
        pool_size=settings.pg_pool_min_size,
        max_overflow=settings.pg_pool_max_size - settings.pg_pool_min_size,
        pool_pre_ping=True,
    )
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def disconnect_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Движок SQLAlchemy ещё не инициализирован")
    return _session_factory


@asynccontextmanager
async def acquire() -> AsyncIterator[AsyncSession]:
    """Используется как FastAPI-зависимость через get_db() ниже."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI-зависимость: `db: AsyncSession = Depends(get_db)`."""
    async with acquire() as session:
        yield session


async def check_connection() -> bool:
    """Используется HealthService для эндпойнта /health."""
    try:
        async with acquire() as session:
            result = await session.execute(text("SELECT 1;"))
            return result.scalar() == 1
    except Exception:
        return False
