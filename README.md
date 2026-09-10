# Aviation Demo API

REST API на FastAPI поверх демо-базы данных авиаперевозок **postgrespro**
(схема `bookings`: аэропорты, самолёты, рейсы, бронирования, билеты,
посадочные талоны). Все ответы — JSON.

## 1. Разворачиваем демо-базу в локальном PostgreSQL

```bash
# 1. Скачайте архив demo-small-en (~21 МБ) с описанием на странице
#    https://postgrespro.ru/education/demodb и распакуйте .sql файл.
#    (Файл называется примерно demo-small-en-YYYYMMDD.sql)

# 2. Создайте базу и накатите скрипт от суперпользователя postgres.
#    Скрипт сам создаёт БД с именем "demo" (DROP DATABASE IF EXISTS + CREATE DATABASE),
#    поэтому просто выполните:
psql -U postgres -f demo-small-en-YYYYMMDD.sql

# 3. Проверьте, что таблицы на месте
psql -U postgres -d demo -c '\dt bookings.*'
```

Ожидаемые таблицы: `airports_data`, `aircrafts_data`, `flights`, `bookings`,
`tickets`, `ticket_flights`, `boarding_passes`, `seats` — плюс несколько
представлений (`airports`, `aircrafts`, `routes`, `flights_v`).

## 2. Настройка приложения

```bash
cp .env.example .env
# при необходимости поправьте PG_HOST / PG_USER / PG_PASSWORD в .env
```

## 3. Установка зависимостей и запуск

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI (интерактивная документация): http://127.0.0.1:8000/docs

## 4. Эндпойнты

| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/v1/airports` | Список всех аэропортов (`?lang=en\|ru`) |
| GET | `/api/v1/airports/{airport_code}` | Детали аэропорта по коду IATA |
| GET | `/api/v1/flights` | Список рейсов (фильтры: `departure_airport`, `arrival_airport`, `status`, `date_from`, `date_to`, пагинация `limit`/`offset`) |
| GET | `/api/v1/flights/{flight_id}` | Детали рейса: маршрут, аэропорты, самолёт, статус, плановое/фактическое время |
| GET | `/api/v1/passengers/{passenger_id}/flights` | Все рейсы пассажира по номеру документа (билет, бронь, маршрут, класс, цена, место) |
| GET | `/api/v1/stats/airports/{airport_code}` | Статистика по аэропорту за период (`date_from`, `date_to`): вылеты/прилёты, задержки, отмены, средняя задержка, топ направлений |
| GET | `/health` | Проверка работоспособности приложения и подключения к БД |

## 5. Примеры

```bash
curl http://127.0.0.1:8000/health

curl http://127.0.0.1:8000/api/v1/airports/SVO

curl "http://127.0.0.1:8000/api/v1/flights?departure_airport=SVO&status=Arrived&limit=5"

curl http://127.0.0.1:8000/api/v1/flights/6223

curl "http://127.0.0.1:8000/api/v1/passengers/8149%20604011/flights"

curl "http://127.0.0.1:8000/api/v1/stats/airports/SVO?date_from=2017-08-01&date_to=2017-08-07"
```

## Структура проекта

```
app/
  config.py     — настройки подключения к БД (переменные окружения / .env)
  database.py   — пул подключений asyncpg
  schemas.py    — Pydantic-модели ответов
  main.py       — FastAPI-приложение и все эндпойнты
requirements.txt
.env.example
```

## Технические заметки

- Подключение к БД — через `asyncpg` с пулом соединений, создаваемым один раз
  при старте приложения (см. `lifespan` в `main.py`), а не на каждый запрос.
- Локализуемые поля (`airport_name`, `city`, `model` самолёта) хранятся в БД
  как `jsonb` с ключами `en`/`ru`; в API это учтено параметром `?lang=`.
- `/api/v1/flights` поддерживает пагинацию и возвращает `total` — общее
  количество рейсов, подходящих под фильтр (для постраничной навигации).
- `/api/v1/stats/airports/{code}` при отсутствии `date_from`/`date_to`
  автоматически берёт весь диапазон дат, присутствующий в демо-данных.
