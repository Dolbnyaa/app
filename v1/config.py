"""
Настройки приложения. Значения по умолчанию рассчитаны на локальный
PostgreSQL с загруженной демо-базой postgrespro (schema `bookings`).
Все параметры можно переопределить переменными окружения или файлом .env.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_db: str = "demo"
    pg_user: str = "postgres"
    pg_password: str = "postgres"

    pg_pool_min_size: int = 1
    pg_pool_max_size: int = 10

    # Язык для локализуемых полей (airport_name, city, aircraft model): "en" или "ru"
    default_lang: str = "en"

    @property
    def dsn(self) -> str:
        return (
            f"postgresql://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )


settings = Settings()
