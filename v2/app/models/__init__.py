"""
Собирает все ORM-модели в одном месте, чтобы их можно было импортировать
как `from app.models import Flight, Airport, ...`, и чтобы все классы
гарантированно были зарегистрированы в реестре Base.registry до того, как
SQLAlchemy попробует разрешить строковые ссылки вида Mapped["Airport"]
внутри relationship() в других модулях.
"""
from app.models.aircraft import Aircraft
from app.models.airport import Airport
from app.models.boarding_pass import BoardingPass
from app.models.booking import Booking
from app.models.flight import Flight
from app.models.seat import Seat
from app.models.ticket import Ticket
from app.models.ticket_flight import TicketFlight

__all__ = [
    "Aircraft",
    "Airport",
    "BoardingPass",
    "Booking",
    "Flight",
    "Seat",
    "Ticket",
    "TicketFlight",
]
