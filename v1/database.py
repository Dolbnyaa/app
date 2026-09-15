"""
Пул подключений к PostgreSQL на базе asyncpg.

Пул создаётся один раз при старте приложения (см. main.py -> lifespan)
и переиспользуется всеми запросами — так же, как это принято делать
в проде, вместо открытия нового соединения на каждый запрос.
"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

import asyncpg

from app.config import settings

_pool: asyncpg.Pool | None = None


async def connect_pool() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.dsn,
        min_size=settings.pg_pool_min_size,
        max_size=settings.pg_pool_max_size,
    )


async def disconnect_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Пул подключений ещё не инициализирован")
    return _pool


@asynccontextmanager
async def acquire() -> AsyncIterator[asyncpg.Connection]:
    pool = get_pool()
    async with pool.acquire() as conn:
        yield conn


async def check_connection() -> bool:
    """Используется эндпойнтом /health."""
    try:
        async with acquire() as conn:
            result = await conn.fetchval("SELECT 1;")
            return result == 1
    except Exception:
        return False
