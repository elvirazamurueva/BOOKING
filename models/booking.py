"""
Модель бронирования для мини-системы бронирования ресторана.
"""

from datetime import datetime


class Booking:
    """Класс бронирования для хранения информации о бронировании стола."""

    def __init__(
        self,
        booking_id: int,
        user_id: int,
        table_id: int,
        booking_date: datetime,
        duration_minutes: int = 90,
        guest_count: int = 1,
        status: str = "confirmed",
        created_at: datetime | None = None,
        notes: str | None = None,
    ):
        self.booking_id = booking_id
        self.user_id = user_id
        self.table_id = table_id
        self.booking_date = booking_date
        self.duration_minutes = duration_minutes
        self.guest_count = guest_count
        self.status = status
        self.created_at = created_at or datetime.now()
        self.notes = notes

    def __repr__(self) -> str:
        return f"Booking(booking_id={self.booking_id}, table_id={self.table_id}, user_id={self.user_id}, date={self.booking_date})"