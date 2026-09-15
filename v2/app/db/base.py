"""Базовый класс декларативных моделей и кастомные типы колонок SQLAlchemy."""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import UserDefinedType


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей — от него наследуются все таблицы."""


class Point(UserDefinedType):
    """
    как превращать Python tuple[float, float] в SQL при
    записи (bind_processor) и как разбирать значение из БД при чтении
    (result_processor).
    """
    cache_ok = True

    def get_col_spec(self, **kw):
        return "POINT"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            lon, lat = value
            return f"({lon},{lat})"
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            if isinstance(value, str):
                x_str, y_str = value.strip("()").split(",")
                return (float(x_str), float(y_str))
            # asyncpg может отдать собственный объект Point с атрибутами .x/.y
            return (float(value.x), float(value.y))
        return process
