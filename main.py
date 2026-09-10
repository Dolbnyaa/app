"""
Aviation Demo API
==================
REST API поверх демо-базы postgrespro (авиаперевозки, схема `bookings`).

Запуск:
    uvicorn app.main:app --reload

Документация (Swagger UI) после запуска: http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import Literal

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import acquire, check_connection, connect_pool, disconnect_pool
from app.schemas import (
    AircraftBrief,
    AirportBrief,
    AirportOut,
    AirportStatsOut,
    FlightDetailOut,
    FlightListItem,
    FlightListOut,
    HealthOut,
    PassengerFlightItem,
    PopularDestination,
)

Lang = Literal["en", "ru"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_pool()
    yield
    await disconnect_pool()


app = FastAPI(
    title="Aviation Demo API",
    description="REST API поверх демо-базы данных авиаперевозок postgrespro",
    version="1.0.0",
    lifespan=lifespan,
)


def point_to_lon_lat(point) -> tuple[float, float]:
    """asyncpg возвращает `point` как объект с атрибутами .x (долгота) и .y (широта)."""
    return float(point.x), float(point.y)


# --------------------------------------------------------------------------
# /health
# --------------------------------------------------------------------------

@app.get("/health", response_model=HealthOut, tags=["health"])
async def health():
    db_ok = await check_connection()
    status_text = "ok" if db_ok else "error"
    payload = HealthOut(status=status_text, database="connected" if db_ok else "unavailable")
    if not db_ok:
        return JSONResponse(status_code=503, content=payload.model_dump())
    return payload


# --------------------------------------------------------------------------
# /api/v1/airports
# --------------------------------------------------------------------------

@app.get("/api/v1/airports", response_model=list[AirportOut], tags=["airports"])
async def list_airports(lang: Lang = Query(settings.default_lang, description="Язык названия: en/ru")):
    query = """
        SELECT airport_code,
               airport_name ->> $1 AS airport_name,
               city ->> $1 AS city,
               coordinates,
               timezone
        FROM bookings.airports_data
        ORDER BY airport_code;
    """
    async with acquire() as conn:
        rows = await conn.fetch(query, lang)

    result = []
    for row in rows:
        lon, lat = point_to_lon_lat(row["coordinates"])
        result.append(
            AirportOut(
                airport_code=row["airport_code"].strip(),
                airport_name=row["airport_name"],
                city=row["city"],
                longitude=lon,
                latitude=lat,
                timezone=row["timezone"],
            )
        )
    return result


@app.get("/api/v1/airports/{airport_code}", response_model=AirportOut, tags=["airports"])
async def get_airport(
    airport_code: str = Path(..., min_length=3, max_length=3, description="Код IATA, напр. SVO"),
    lang: Lang = Query(settings.default_lang),
):
    query = """
        SELECT airport_code,
               airport_name ->> $1 AS airport_name,
               city ->> $1 AS city,
               coordinates,
               timezone
        FROM bookings.airports_data
        WHERE airport_code = $2;
    """
    async with acquire() as conn:
        row = await conn.fetchrow(query, lang, airport_code.upper())

    if row is None:
        raise HTTPException(status_code=404, detail=f"Аэропорт '{airport_code}' не найден")

    lon, lat = point_to_lon_lat(row["coordinates"])
    return AirportOut(
        airport_code=row["airport_code"].strip(),
        airport_name=row["airport_name"],
        city=row["city"],
        longitude=lon,
        latitude=lat,
        timezone=row["timezone"],
    )


# --------------------------------------------------------------------------
# /api/v1/flights
# --------------------------------------------------------------------------

@app.get("/api/v1/flights", response_model=FlightListOut, tags=["flights"])
async def list_flights(
    departure_airport: str | None = Query(None, min_length=3, max_length=3),
    arrival_airport: str | None = Query(None, min_length=3, max_length=3),
    status: str | None = Query(None, description="On Time / Delayed / Departed / Arrived / Scheduled / Cancelled"),
    date_from: datetime | None = Query(None, description="Фильтр по scheduled_departure, включительно"),
    date_to: datetime | None = Query(None, description="Фильтр по scheduled_departure, включительно"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    conditions = []
    params: list = []

    def add_condition(sql: str, value) -> None:
        params.append(value)
        conditions.append(sql.format(idx=len(params)))

    if departure_airport:
        add_condition("departure_airport = ${idx}", departure_airport.upper())
    if arrival_airport:
        add_condition("arrival_airport = ${idx}", arrival_airport.upper())
    if status:
        add_condition("status = ${idx}", status)
    if date_from:
        add_condition("scheduled_departure >= ${idx}", date_from)
    if date_to:
        add_condition("scheduled_departure <= ${idx}", date_to)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_query = f"SELECT count(*) FROM bookings.flights {where_clause};"

    list_query = f"""
        SELECT flight_id, flight_no, scheduled_departure, scheduled_arrival,
               departure_airport, arrival_airport, status, aircraft_code
        FROM bookings.flights
        {where_clause}
        ORDER BY scheduled_departure
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2};
    """

    async with acquire() as conn:
        total = await conn.fetchval(count_query, *params)
        rows = await conn.fetch(list_query, *params, limit, offset)

    items = [
        FlightListItem(
            flight_id=row["flight_id"],
            flight_no=row["flight_no"].strip(),
            scheduled_departure=row["scheduled_departure"],
            scheduled_arrival=row["scheduled_arrival"],
            departure_airport=row["departure_airport"].strip(),
            arrival_airport=row["arrival_airport"].strip(),
            status=row["status"],
            aircraft_code=row["aircraft_code"].strip(),
        )
        for row in rows
    ]

    return FlightListOut(total=total, limit=limit, offset=offset, items=items)


@app.get("/api/v1/flights/{flight_id}", response_model=FlightDetailOut, tags=["flights"])
async def get_flight(flight_id: int, lang: Lang = Query(settings.default_lang)):
    query = """
        SELECT
            f.flight_id, f.flight_no, f.status,
            f.scheduled_departure, f.scheduled_arrival,
            f.actual_departure, f.actual_arrival,
            dep.airport_code AS dep_code, dep.airport_name ->> $2 AS dep_name, dep.city ->> $2 AS dep_city,
            arr.airport_code AS arr_code, arr.airport_name ->> $2 AS arr_name, arr.city ->> $2 AS arr_city,
            ac.aircraft_code, ac.model ->> $2 AS aircraft_model, ac.range AS aircraft_range
        FROM bookings.flights f
        JOIN bookings.airports_data dep ON dep.airport_code = f.departure_airport
        JOIN bookings.airports_data arr ON arr.airport_code = f.arrival_airport
        JOIN bookings.aircrafts_data ac ON ac.aircraft_code = f.aircraft_code
        WHERE f.flight_id = $1;
    """
    async with acquire() as conn:
        row = await conn.fetchrow(query, flight_id, lang)

    if row is None:
        raise HTTPException(status_code=404, detail=f"Рейс с id={flight_id} не найден")

    return FlightDetailOut(
        flight_id=row["flight_id"],
        flight_no=row["flight_no"].strip(),
        status=row["status"],
        departure_airport=AirportBrief(
            airport_code=row["dep_code"].strip(), airport_name=row["dep_name"], city=row["dep_city"]
        ),
        arrival_airport=AirportBrief(
            airport_code=row["arr_code"].strip(), airport_name=row["arr_name"], city=row["arr_city"]
        ),
        aircraft=AircraftBrief(
            aircraft_code=row["aircraft_code"].strip(),
            model=row["aircraft_model"],
            range=row["aircraft_range"],
        ),
        scheduled_departure=row["scheduled_departure"],
        scheduled_arrival=row["scheduled_arrival"],
        actual_departure=row["actual_departure"],
        actual_arrival=row["actual_arrival"],
    )


# --------------------------------------------------------------------------
# /api/v1/passengers/{passenger_id}/flights
# --------------------------------------------------------------------------

@app.get(
    "/api/v1/passengers/{passenger_id}/flights",
    response_model=list[PassengerFlightItem],
    tags=["passengers"],
)
async def get_passenger_flights(
    passenger_id: str = Path(..., description="Номер документа пассажира, напр. '4098 174300'"),
):
    query = """
        SELECT
            t.ticket_no, t.book_ref,
            f.flight_id, f.flight_no, f.departure_airport, f.arrival_airport,
            f.scheduled_departure, f.scheduled_arrival, f.status,
            tf.fare_conditions, tf.amount,
            bp.seat_no
        FROM bookings.tickets t
        JOIN bookings.ticket_flights tf ON tf.ticket_no = t.ticket_no
        JOIN bookings.flights f ON f.flight_id = tf.flight_id
        LEFT JOIN bookings.boarding_passes bp
               ON bp.ticket_no = tf.ticket_no AND bp.flight_id = tf.flight_id
        WHERE t.passenger_id = $1
        ORDER BY f.scheduled_departure;
    """
    async with acquire() as conn:
        rows = await conn.fetch(query, passenger_id)

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Пассажир с номером документа '{passenger_id}' не найден или у него нет рейсов",
        )

    return [
        PassengerFlightItem(
            ticket_no=row["ticket_no"].strip(),
            book_ref=row["book_ref"].strip(),
            flight_id=row["flight_id"],
            flight_no=row["flight_no"].strip(),
            departure_airport=row["departure_airport"].strip(),
            arrival_airport=row["arrival_airport"].strip(),
            scheduled_departure=row["scheduled_departure"],
            scheduled_arrival=row["scheduled_arrival"],
            status=row["status"],
            fare_conditions=row["fare_conditions"],
            amount=Decimal(row["amount"]),
            seat_no=row["seat_no"].strip() if row["seat_no"] else None,
        )
        for row in rows
    ]


# --------------------------------------------------------------------------
# /api/v1/stats/airports/{airport_code}
# --------------------------------------------------------------------------

@app.get(
    "/api/v1/stats/airports/{airport_code}",
    response_model=AirportStatsOut,
    tags=["stats"],
)
async def get_airport_stats(
    airport_code: str = Path(..., min_length=3, max_length=3),
    date_from: datetime | None = Query(None, description="Начало периода. По умолчанию — вся история"),
    date_to: datetime | None = Query(None, description="Конец периода. По умолчанию — вся история"),
    top_n: int = Query(5, ge=1, le=20, description="Сколько популярных направлений вернуть"),
):
    code = airport_code.upper()

    async with acquire() as conn:
        exists = await conn.fetchval(
            "SELECT 1 FROM bookings.airports_data WHERE airport_code = $1;", code
        )
        if not exists:
            raise HTTPException(status_code=404, detail=f"Аэропорт '{airport_code}' не найден")

        # Если период не задан — берём весь диапазон дат в базе.
        if date_from is None or date_to is None:
            bounds = await conn.fetchrow(
                "SELECT min(scheduled_departure) AS lo, max(scheduled_departure) AS hi FROM bookings.flights;"
            )
            date_from = date_from or bounds["lo"]
            date_to = date_to or bounds["hi"]

        stats_query = """
            SELECT
                count(*) FILTER (WHERE departure_airport = $1) AS departures_count,
                count(*) FILTER (WHERE arrival_airport = $1) AS arrivals_count,
                count(*) FILTER (WHERE departure_airport = $1 AND status = 'Delayed') AS delayed_count,
                count(*) FILTER (WHERE departure_airport = $1 AND status = 'Cancelled') AS cancelled_count,
                avg(EXTRACT(EPOCH FROM (actual_departure - scheduled_departure)) / 60.0)
                    FILTER (WHERE departure_airport = $1 AND actual_departure IS NOT NULL
                             AND actual_departure > scheduled_departure) AS avg_delay_minutes
            FROM bookings.flights
            WHERE (departure_airport = $1 OR arrival_airport = $1)
              AND scheduled_departure BETWEEN $2 AND $3;
        """
        stats_row = await conn.fetchrow(stats_query, code, date_from, date_to)

        popular_query = """
            SELECT f.arrival_airport AS airport_code,
                   a.airport_name ->> 'en' AS airport_name,
                   count(*) AS flights_count
            FROM bookings.flights f
            JOIN bookings.airports_data a ON a.airport_code = f.arrival_airport
            WHERE f.departure_airport = $1
              AND f.scheduled_departure BETWEEN $2 AND $3
            GROUP BY f.arrival_airport, a.airport_name ->> 'en'
            ORDER BY count(*) DESC
            LIMIT $4;
        """
        popular_rows = await conn.fetch(popular_query, code, date_from, date_to, top_n)

    return AirportStatsOut(
        airport_code=code,
        period_from=date_from,
        period_to=date_to,
        departures_count=stats_row["departures_count"],
        arrivals_count=stats_row["arrivals_count"],
        delayed_count=stats_row["delayed_count"],
        cancelled_count=stats_row["cancelled_count"],
        avg_delay_minutes=(
            round(stats_row["avg_delay_minutes"], 1) if stats_row["avg_delay_minutes"] is not None else None
        ),
        popular_destinations=[
            PopularDestination(
                airport_code=row["airport_code"].strip(),
                airport_name=row["airport_name"],
                flights_count=row["flights_count"],
            )
            for row in popular_rows
        ],
    )
