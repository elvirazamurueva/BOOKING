"""
PostgreSQL Database Driver Module
Модуль для работы с базой данных PostgreSQL с CRUD-операциями
"""

import psycopg2
from psycopg2 import Error, sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from typing import Optional, List, Dict, Any, Type
import inspect

# Загрузка переменных окружения
load_dotenv()


class PostgreSQLDatabase:
    """
    Класс для работы с PostgreSQL базой данных.
    Предоставляет CRUD-операции для таблицы users.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Инициализация подключения к PostgreSQL.
        
        Args:
            host: Адрес сервера (по умолчанию из .env)
            port: Порт (по умолчанию из .env)
            database: Имя базы данных (по умолчанию из .env)
            user: Имя пользователя (по умолчанию из .env)
            password: Пароль (по умолчанию из .env)
        """
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = port or int(os.getenv("POSTGRES_PORT", 5432))
        self.database = database or os.getenv("POSTGRES_DB")
        self.user = user or os.getenv("POSTGRES_USER")
        self.password = password or os.getenv("POSTGRES_PASSWORD")
        
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """
        Установить подключение к базе данных.
        
        Returns:
            bool: True если подключение успешно, False иначе
        """
        try:
            print("Подключение к PostgreSQL...")
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("Успешно подключено!")
            return True
        except (Exception, Error) as error:
            print(f"Ошибка при подключении к PostgreSQL: {error}")
            return False

    def close(self) -> None:
        """Закрыть подключение к базе данных."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Соединение закрыто")

    def __enter__(self):
        """Контекстный менеджер: вход."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер: выход."""
        self.close()

    # ==================== TABLE CREATION ====================

    def create_table_from_model(self, model_class: Type) -> bool:
        """
        Создать таблицу в БД на основе класса модели (если она не существует).
        
        Args:
            model_class: Класс модели (User, Table, Booking и т.д.)
            
        Returns:
            True если таблица создана или уже существует, False при ошибке
        """
        try:
            # Получаем имя таблицы из класса модели
            # Если есть __tablename__, используем его, иначе генерируем из имени класса
            if hasattr(model_class, '__tablename__'):
                table_name = model_class.__tablename__
            else:
                table_name = model_class.__name__.lower() + 's'
            
            # Получаем параметры __init__ метода модели
            init_signature = inspect.signature(model_class.__init__)
            parameters = init_signature.parameters
            
            # Строим определения колонок
            columns = []
            
            for param_name, param in parameters.items():
                # Пропускаем self
                if param_name == 'self':
                    continue
                
                # Получаем аннотацию типа
                annotation = param.annotation
                
                # Определяем SQL тип и NULL/NOT NULL
                sql_type = "TEXT"
                nullable = "NULL"
                default_value = ""
                
                # Проверяем, является ли тип Optional (т.е. X | None)
                type_str = str(annotation)
                
                if 'int' in type_str and 'None' not in type_str:
                    sql_type = "INTEGER"
                    nullable = "NOT NULL"
                elif 'str' in type_str and 'None' not in type_str:
                    sql_type = "VARCHAR(255)"
                    nullable = "NOT NULL"
                elif 'bool' in type_str and 'None' not in type_str:
                    sql_type = "BOOLEAN"
                    nullable = "NOT NULL"
                    # Для boolean полей без значения по умолчанию ставим TRUE
                    default_value = " DEFAULT true"
                elif 'datetime' in type_str:
                    sql_type = "TIMESTAMP"
                    nullable = "NULL" if 'None' in type_str else "NOT NULL"
                    if 'created_at' in param_name:
                        default_value = " DEFAULT CURRENT_TIMESTAMP"
                elif 'None' not in type_str:
                    # По умолчанию для обязательных полей
                    if 'int' in type_str:
                        sql_type = "INTEGER"
                    elif 'str' in type_str:
                        sql_type = "VARCHAR(255)"
                    nullable = "NOT NULL"
                else:
                    # Опциональное поле
                    nullable = "NULL"
                
                # Определяем, является ли поле первичным ключом
                is_primary_key = param_name in ('id', 'user_id', 'table_id', 'booking_id')
                
                # Для первичных ключей используем SERIAL для автоинкремента
                if is_primary_key and 'int' in type_str:
                    sql_type = "SERIAL"
                    nullable = "NOT NULL"
                
                col_def = f"{param_name} {sql_type} {nullable}"
                if default_value:
                    col_def += default_value
                columns.append(col_def)
            
            # Создаём CREATE TABLE запрос
            columns_sql = ",\n    ".join(columns)
            query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {columns_sql}
                );
            """
            
            self.cursor.execute(query)
            self.connection.commit()
            print(f"Таблица '{table_name}' успешно создана (или уже существует)")
            return True
            
        except (Exception, Error) as error:
            print(f"Ошибка при создании таблицы: {error}")
            self.connection.rollback()
            return False

    def drop_table(self, table_name: str) -> bool:
        """
        Удалить таблицу из БД.
        
        Args:
            table_name: Имя таблицы
            
        Returns:
            True если таблица удалена, False при ошибке
        """
        try:
            query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
            self.cursor.execute(query)
            self.connection.commit()
            print(f"Таблица '{table_name}' удалена")
            return True
        except (Exception, Error) as error:
            print(f"Ошибка при удалении таблицы: {error}")
            self.connection.rollback()
            return False

    def recreate_table_from_model(self, model_class: Type) -> bool:
        """
        Удалить и пересоздать таблицу на основе модели.
        
        Args:
            model_class: Класс модели (User, Table, Booking и т.д.)
            
        Returns:
            True если таблица успешно пересоздана, False при ошибке
        """
        table_name = model_class.__name__.lower() + 's'
        self.drop_table(table_name)
        return self.create_table_from_model(model_class)

    # ==================== CREATE ====================

    def create_user(self, name: str, age: int) -> Optional[int]:
        """
        Создать нового пользователя.
        
        Args:
            name: Имя пользователя
            age: Возраст пользователя
            
        Returns:
            int: ID созданного пользователя или None при ошибке
        """
        try:
            query = """
                INSERT INTO users (name, age)
                VALUES (%s, %s)
                RETURNING id;
            """
            self.cursor.execute(query, (name, age))
            self.connection.commit()
            result = self.cursor.fetchone()
            return result['id'] if result else None
        except (Exception, Error) as error:
            print(f"Ошибка при создании пользователя: {error}")
            self.connection.rollback()
            return None

    # ==================== READ ====================

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict с данными пользователя или None
        """
        try:
            query = "SELECT * FROM users WHERE id = %s;"
            self.cursor.execute(query, (user_id,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except (Exception, Error) as error:
            print(f"Ошибка при получении пользователя: {error}")
            return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Получить всех пользователей.
        
        Returns:
            Список всех пользователей
        """
        try:
            query = "SELECT * FROM users ORDER BY id;"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при получении пользователей: {error}")
            return []

    def get_users_by_age(self, min_age: Optional[int] = None, max_age: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получить пользователей по диапазону возрастов.
        
        Args:
            min_age: Минимальный возраст (необязательно)
            max_age: Максимальный возраст (необязательно)
            
        Returns:
            Список пользователей
        """
        try:
            query = "SELECT * FROM users WHERE 1=1"
            params = []
            
            if min_age is not None:
                query += " AND age >= %s"
                params.append(min_age)
            
            if max_age is not None:
                query += " AND age <= %s"
                params.append(max_age)
            
            query += " ORDER BY id;"
            
            self.cursor.execute(query, tuple(params) if params else None)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при получении пользователей: {error}")
            return []

    def search_users_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """
        Поиск пользователей по имени (частичное совпадение).
        
        Args:
            name_pattern: Паттерн имени (например, 'Иван')
            
        Returns:
            Список найденных пользователей
        """
        try:
            query = """
                SELECT * FROM users 
                WHERE name ILIKE %s
                ORDER BY id;
            """
            self.cursor.execute(query, (f"%{name_pattern}%",))
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при поиске пользователей: {error}")
            return []

    def search_users_by_username(self, username_pattern: str) -> List[Dict[str, Any]]:
        """
        Поиск пользователей по username (частичное совпадение).
        
        Args:
            username_pattern: Паттерн username (например, 'ivan')
            
        Returns:
            Список найденных пользователей
        """
        try:
            query = """
                SELECT * FROM users 
                WHERE username ILIKE %s
                ORDER BY user_id;
            """
            self.cursor.execute(query, (f"%{username_pattern}%",))
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при поиске пользователей: {error}")
            return []

    # ==================== USER CRUD METHODS ====================

    def create_user(self, username: str, email: str, phone: Optional[str] = None, 
                    first_name: Optional[str] = None, last_name: Optional[str] = None) -> Optional[int]:
        """
        Создать нового пользователя.
        
        Args:
            username: Имя пользователя
            email: Email пользователя
            phone: Телефон (необязательно)
            first_name: Имя (необязательно)
            last_name: Фамилия (необязательно)
            
        Returns:
            int: ID созданного пользователя или None при ошибке
        """
        try:
            query = """
                INSERT INTO users (username, email, phone, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING user_id;
            """
            self.cursor.execute(query, (username, email, phone, first_name, last_name))
            self.connection.commit()
            result = self.cursor.fetchone()
            return result['user_id'] if result else None
        except (Exception, Error) as error:
            print(f"Ошибка при создании пользователя: {error}")
            self.connection.rollback()
            return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Получить всех пользователей.
        
        Returns:
            Список всех пользователей
        """
        try:
            query = "SELECT * FROM users ORDER BY user_id;"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при получении пользователей: {error}")
            return []

    def update_user(self, user_id: int, username: Optional[str] = None, 
                    email: Optional[str] = None, phone: Optional[str] = None,
                    first_name: Optional[str] = None, last_name: Optional[str] = None) -> bool:
        """
        Обновить данные пользователя.
        
        Args:
            user_id: ID пользователя
            username: Новое имя пользователя (необязательно)
            email: Новый email (необязательно)
            phone: Новый телефон (необязательно)
            first_name: Новое имя (необязательно)
            last_name: Новая фамилия (необязательно)
            
        Returns:
            True если обновлено, False иначе
        """
        try:
            updates = []
            params = []
            
            if username is not None:
                updates.append("username = %s")
                params.append(username)
            
            if email is not None:
                updates.append("email = %s")
                params.append(email)
            
            if phone is not None:
                updates.append("phone = %s")
                params.append(phone)
            
            if first_name is not None:
                updates.append("first_name = %s")
                params.append(first_name)
            
            if last_name is not None:
                updates.append("last_name = %s")
                params.append(last_name)
            
            if not updates:
                return False
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s;"
            
            self.cursor.execute(query, tuple(params))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except (Exception, Error) as error:
            print(f"Ошибка при обновлении пользователя: {error}")
            self.connection.rollback()
            return False

    def delete_user(self, user_id: int) -> bool:
        """
        Удалить пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если удалено, False иначе
        """
        try:
            query = "DELETE FROM users WHERE user_id = %s;"
            self.cursor.execute(query, (user_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except (Exception, Error) as error:
            print(f"Ошибка при удалении пользователя: {error}")
            self.connection.rollback()
            return False

    # ==================== TABLE CRUD METHODS ====================

    def get_all_tables(self) -> List[Dict[str, Any]]:
        """
        Получить все столы.
        
        Returns:
            Список всех столов
        """
        try:
            query = "SELECT * FROM restaurant_tables ORDER BY table_number;"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при получении столов: {error}")
            return []

    def get_available_tables(self, min_seats: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получить доступные столы.
        
        Args:
            min_seats: Минимальное количество мест (необязательно)
            
        Returns:
            Список доступных столов
        """
        try:
            query = "SELECT * FROM restaurant_tables WHERE is_available = true"
            params = []
            
            if min_seats is not None:
                query += " AND seats >= %s"
                params.append(min_seats)
            
            query += " ORDER BY table_number;"
            
            self.cursor.execute(query, tuple(params) if params else None)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при получении доступных столов: {error}")
            return []

    def get_table_by_id(self, table_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить стол по ID.
        
        Args:
            table_id: ID стола
            
        Returns:
            Dict с данными стола или None
        """
        try:
            query = "SELECT * FROM restaurant_tables WHERE table_id = %s;"
            self.cursor.execute(query, (table_id,))
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except (Exception, Error) as error:
            print(f"Ошибка при получении стола: {error}")
            return None

    def update_table_status(self, table_id: int, is_available: bool) -> bool:
        """
        Обновить статус доступности стола.
        
        Args:
            table_id: ID стола
            is_available: Статус доступности
            
        Returns:
            True если обновлено, False иначе
        """
        try:
            query = "UPDATE restaurant_tables SET is_available = %s WHERE table_id = %s;"
            self.cursor.execute(query, (is_available, table_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except (Exception, Error) as error:
            print(f"Ошибка при обновлении статуса стола: {error}")
            self.connection.rollback()
            return False

    def delete_table(self, table_id: int) -> bool:
        """
        Удалить стол по ID.
        
        Args:
            table_id: ID стола
            
        Returns:
            True если удалено, False иначе
        """
        try:
            query = "DELETE FROM restaurant_tables WHERE table_id = %s;"
            self.cursor.execute(query, (table_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except (Exception, Error) as error:
            print(f"Ошибка при удалении стола: {error}")
            self.connection.rollback()
            return False

    # ==================== BOOKING CRUD METHODS ====================

    def get_all_bookings(self) -> List[Dict[str, Any]]:
        """
        Получить все бронирования.
        
        Returns:
            Список всех бронирований
        """
        try:
            query = "SELECT * FROM bookings ORDER BY booking_date DESC;"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при получении бронирований: {error}")
            return []

    def get_bookings_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Получить бронирования по статусу.
        
        Args:
            status: Статус бронирования
            
        Returns:
            Список бронирований
        """
        try:
            query = "SELECT * FROM bookings WHERE status = %s ORDER BY booking_date DESC;"
            self.cursor.execute(query, (status,))
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при получении бронирований: {error}")
            return []

    def get_bookings_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получить бронирования пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список бронирований
        """
        try:
            query = "SELECT * FROM bookings WHERE user_id = %s ORDER BY booking_date DESC;"
            self.cursor.execute(query, (user_id,))
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при получении бронирований пользователя: {error}")
            return []

    def get_bookings_by_table(self, table_id: int) -> List[Dict[str, Any]]:
        """
        Получить бронирования стола.
        
        Args:
            table_id: ID стола
            
        Returns:
            Список бронирований
        """
        try:
            query = "SELECT * FROM bookings WHERE table_id = %s ORDER BY booking_date DESC;"
            self.cursor.execute(query, (table_id,))
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except (Exception, Error) as error:
            print(f"Ошибка при получении бронирований стола: {error}")
            return []

    def check_booking_conflict(self, table_id: int, booking_date: datetime, duration_minutes: int, 
                                exclude_booking_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Проверить есть ли конфликт бронирований для стола.
        
        Args:
            table_id: ID стола
            booking_date: Дата и время бронирования
            duration_minutes: Длительность в минутах
            exclude_booking_id: ID бронирования для исключения (при обновлении)
            
        Returns:
            Конфликтующее бронирование или None
        """
        try:
            # Вычисляем конечное время
            from datetime import timedelta
            end_time = booking_date + timedelta(minutes=duration_minutes)
            
            # Проверка на пересечение временных интервалов
            # Бронирование А конфликтует с Б если: A_start < B_end AND A_end > B_start
            query = """
                SELECT * FROM bookings 
                WHERE table_id = %s 
                AND status = 'confirmed'
                AND booking_date < %s 
                AND (booking_date + (duration_minutes || ' minutes')::interval) > %s
            """
            
            params = (table_id, end_time, booking_date)
            
            if exclude_booking_id:
                query += " AND booking_id != %s"
                params = (table_id, end_time, booking_date, exclude_booking_id)
            
            self.cursor.execute(query, params)
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except (Exception, Error) as error:
            print(f"Ошибка при проверке конфликта бронирований: {error}")
            return None

    def update_booking_status(self, booking_id: int, status: str) -> bool:
        """
        Обновить статус бронирования.
        
        Args:
            booking_id: ID бронирования
            status: Новый статус
            
        Returns:
            True если обновлено, False иначе
        """
        try:
            query = "UPDATE bookings SET status = %s WHERE booking_id = %s;"
            self.cursor.execute(query, (status, booking_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except (Exception, Error) as error:
            print(f"Ошибка при обновлении статуса бронирования: {error}")
            self.connection.rollback()
            return False

    def delete_booking(self, booking_id: int) -> bool:
        """
        Удалить бронирование по ID.
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            True если удалено, False иначе
        """
        try:
            query = "DELETE FROM bookings WHERE booking_id = %s;"
            self.cursor.execute(query, (booking_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except (Exception, Error) as error:
            print(f"Ошибка при удалении бронирования: {error}")
            self.connection.rollback()
            return False

    # ==================== GENERIC METHODS ====================

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Any:
        """
        Выполнить произвольный SELECT-запрос.
        
        Args:
            query: SQL-запрос
            params: Параметры запроса (необязательно)
            
        Returns:
            Результаты запроса или None
        """
        try:
            self.cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                return [dict(row) for row in self.cursor.fetchall()]
            return True
        except (Exception, Error) as error:
            print(f"Ошибка при выполнении запроса: {error}")
            return None

    def execute_command(self, query: str, params: Optional[tuple] = None) -> bool:
        """
        Выполнить произвольный INSERT/UPDATE/DELETE-запрос.
        
        Args:
            query: SQL-запрос
            params: Параметры запроса (необязательно)
            
        Returns:
            True если успешно, False иначе
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except (Exception, Error) as error:
            print(f"Ошибка при выполнении команды: {error}")
            self.connection.rollback()
            return False

    def get_table_names(self) -> List[str]:
        """
        Получить список всех таблиц в базе данных.
        
        Returns:
            Список названий таблиц
        """
        try:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """
            self.cursor.execute(query)
            return [row['table_name'] for row in self.cursor.fetchall()]
        except (Exception, Error) as error:
            print(f"Ошибка при получении таблиц: {error}")
            return []
