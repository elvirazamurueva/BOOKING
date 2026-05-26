"""
Модель пользователя для мини-системы бронирования.
"""


class User:
    """Класс пользователя для хранения информации о пользователе."""

    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        phone: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_active: bool = True,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.phone = phone
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = is_active

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id}, username='{self.username}')"