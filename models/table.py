"""
Модель стола для мини-системы бронирования ресторана.
"""


class Table:
    """Класс стола для хранения информации о столе в ресторане."""

    # Имя таблицы в БД (избегаем конфликта с зарезервированным словом 'tables')
    __tablename__ = 'restaurant_tables'

    def __init__(
        self,
        table_id: int,
        table_number: int,
        seats: int,
        location: str | None = None,
        is_available: bool = True,
    ):
        self.table_id = table_id
        self.table_number = table_number
        self.seats = seats
        self.location = location
        self.is_available = is_available

    def __repr__(self) -> str:
        return f"Table(table_id={self.table_id}, number={self.table_number}, seats={self.seats})"