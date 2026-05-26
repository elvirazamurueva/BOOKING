from db_driver import PostgreSQLDatabase
from models.booking import Booking
from models.table import Table
from models.user import User
from datetime import datetime
from typing import Optional, List, Dict, Any


class BookingSystem:
    """Класс системы бронирования с удобными методами."""

    def __init__(self):
        self.db = PostgreSQLDatabase()

    def connect(self) -> bool:
        """Подключиться к базе данных."""
        return self.db.connect()

    def close(self):
        """Закрыть подключение к базе данных."""
        self.db.close()

    # ==================== TABLE SETUP ====================

    def create_tables(self):
        """Создать таблицы в БД на основе моделей."""
        if not self.db.connection:
            self.connect()
        
        self.db.create_table_from_model(User)    
        self.db.create_table_from_model(Table)
        self.db.create_table_from_model(Booking)

    def recreate_tables(self):
        """Удалить и пересоздать все таблицы (теряются все данные!)."""
        if not self.db.connection:
            self.connect()
        
        print("Пересоздание таблиц...")
        self.db.recreate_table_from_model(Booking)
        self.db.recreate_table_from_model(Table)
        self.db.recreate_table_from_model(User)
        print("Таблицы пересозданы!")

    # ==================== USER OPERATIONS ====================

    def create_user(self, username: str, email: str, phone: Optional[str] = None,
                    first_name: Optional[str] = None, last_name: Optional[str] = None) -> Optional[int]:
        """Создать нового пользователя."""
        if not self.db.connection:
            self.connect()
        return self.db.create_user(username, email, phone, first_name, last_name)

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Получить всех пользователей."""
        if not self.db.connection:
            self.connect()
        return self.db.get_all_users()

    def search_users_by_username(self, username_pattern: str) -> List[Dict[str, Any]]:
        """Поиск пользователей по username."""
        if not self.db.connection:
            self.connect()
        return self.db.search_users_by_username(username_pattern)

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновить данные пользователя."""
        if not self.db.connection:
            self.connect()
        return self.db.update_user(user_id, **kwargs)

    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя."""
        if not self.db.connection:
            self.connect()
        return self.db.delete_user(user_id)

    # ==================== TABLE OPERATIONS ====================

    def get_all_tables(self) -> List[Dict[str, Any]]:
        """Получить все столы."""
        if not self.db.connection:
            self.connect()
        return self.db.get_all_tables()

    def get_available_tables(self, min_seats: Optional[int] = None) -> List[Dict[str, Any]]:
        """Получить доступные столы."""
        if not self.db.connection:
            self.connect()
        return self.db.get_available_tables(min_seats)

    def get_table_by_id(self, table_id: int) -> Optional[Dict[str, Any]]:
        """Получить стол по ID."""
        if not self.db.connection:
            self.connect()
        return self.db.get_table_by_id(table_id)

    def update_table_status(self, table_id: int, is_available: bool) -> bool:
        """Обновить статус доступности стола."""
        if not self.db.connection:
            self.connect()
        return self.db.update_table_status(table_id, is_available)

    def delete_table(self, table_id: int) -> bool:
        """Удалить стол."""
        if not self.db.connection:
            self.connect()
        return self.db.delete_table(table_id)

    # ==================== BOOKING OPERATIONS ====================

    def get_all_bookings(self) -> List[Dict[str, Any]]:
        """Получить все бронирования."""
        if not self.db.connection:
            self.connect()
        return self.db.get_all_bookings()

    def get_bookings_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Получить бронирования по статусу."""
        if not self.db.connection:
            self.connect()
        return self.db.get_bookings_by_status(status)

    def get_bookings_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить бронирования пользователя."""
        if not self.db.connection:
            self.connect()
        return self.db.get_bookings_by_user(user_id)

    def get_bookings_by_table(self, table_id: int) -> List[Dict[str, Any]]:
        """Получить бронирования стола."""
        if not self.db.connection:
            self.connect()
        return self.db.get_bookings_by_table(table_id)

    def update_booking_status(self, booking_id: int, status: str) -> bool:
        """Обновить статус бронирования."""
        if not self.db.connection:
            self.connect()
        return self.db.update_booking_status(booking_id, status)

    def delete_booking(self, booking_id: int) -> bool:
        """Удалить бронирование."""
        if not self.db.connection:
            self.connect()
        return self.db.delete_booking(booking_id)


def create_tables():
    """Создать таблицы в БД на основе моделей."""
    system = BookingSystem()
    system.create_tables()


def recreate_tables():
    """Удалить и пересоздать все таблицы."""
    system = BookingSystem()
    system.recreate_tables()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--recreate":
        recreate_tables()
    else:
        create_tables()
    
    

