# PostgreSQL Database Driver

Модуль для работы с базой данных PostgreSQL с CRUD-операциями для системы бронирования столов в ресторане.

## Установка

1. Установите зависимости:
```bash
pip install psycopg2-binary python-dotenv
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ваша_база
POSTGRES_USER=ваш_пользователь
POSTGRES_PASSWORD=ваш_пароль
```

## Структура проекта

- `db_driver.py` - Драйвер PostgreSQL с CRUD-операциями
- `backend.py` - Бэкенд системы бронирования
- `gui.py` - Графический интерфейс на tkinter
- `models/` - Модели данных (User, Table, Booking)

## Использование

### Создание таблиц в БД

```bash
python backend.py
```

### Пересоздание таблиц (удалит все данные!)

```bash
python backend.py --recreate
```

### Запуск графического интерфейса

```bash
python gui.py
```

## Графический интерфейс (GUI)

GUI приложение содержит 4 вкладки:

### 1. Вкладка "Пользователи"
- Добавление новых пользователей (username, email, телефон, имя, фамилия)
- Поиск пользователей по username
- Просмотр всех пользователей
- Обновление данных пользователя
- Удаление пользователей

### 2. Вкладка "Столы"
- Добавление новых столов (номер, количество мест, расположение)
- Просмотр всех столов
- Изменение статуса доступности стола
- Удаление столов

### 3. Вкладка "Бронирования"
- Создание бронирований (выбор пользователя, стола, дата, длительность, количество гостей, статус, заметки)
- Просмотр всех бронирований
- Фильтрация по статусу (confirmed, completed, cancelled)
- Изменение статуса бронирования
- Отмена бронирования
- Удаление бронирований

### 4. Вкладка "Статус системы"
- Информация о подключении к базе данных
- Статистика: количество пользователей, столов, бронирований
- Количество доступных столов
- Количество активных и отмененных бронирований

## Модели данных

### User (Пользователь)
- user_id - ID пользователя
- username - Имя пользователя
- email - Email
- phone - Телефон
- first_name - Имя
- last_name - Фамилия
- is_active - Активен ли пользователь

### Table (Стол)
- table_id - ID стола
- table_number - Номер стола
- seats - Количество мест
- location - Расположение
- is_available - Доступен ли стол

### Booking (Бронирование)
- booking_id - ID бронирования
- user_id - ID пользователя
- table_id - ID стола
- booking_date - Дата и время бронирования
- duration_minutes - Длительность в минутах
- guest_count - Количество гостей
- status - Статус (confirmed, completed, cancelled)
- notes - Заметки
- created_at - Дата создания

## API Драйвера БД

### CRUD для пользователей
- `create_user(username, email, phone, first_name, last_name)` - Создать пользователя
- `get_all_users()` - Получить всех пользователей
- `search_users_by_username(pattern)` - Поиск по username
- `update_user(user_id, **kwargs)` - Обновить пользователя
- `delete_user(user_id)` - Удалить пользователя

### CRUD для столов
- `get_all_tables()` - Получить все столы
- `get_available_tables(min_seats)` - Получить доступные столы
- `get_table_by_id(table_id)` - Получить стол по ID
- `update_table_status(table_id, is_available)` - Обновить статус стола
- `delete_table(table_id)` - Удалить стол

### CRUD для бронирований
- `get_all_bookings()` - Получить все бронирования
- `get_bookings_by_status(status)` - Получить по статусу
- `get_bookings_by_user(user_id)` - Получить бронирования пользователя
- `get_bookings_by_table(table_id)` - Получить бронирования стола
- `update_booking_status(booking_id, status)` - Обновить статус
- `delete_booking(booking_id)` - Удалить бронирование

## Примеры использования

### Базовое подключение

```python
from db_driver import PostgreSQLDatabase

# Использование через контекстный менеджер (рекомендуется)
with PostgreSQLDatabase() as db:
    users = db.get_all_users()
```

### Использование через BookingSystem

```python
from backend import BookingSystem

system = BookingSystem()
system.create_tables()  # Создать таблицы

# Добавить пользователя
user_id = system.create_user(username="ivan", email="ivan@example.com")

# Добавить стол
tables = system.get_available_tables(min_seats=4)

# Создать бронирование
# (через GUI - проще и нагляднее)
```

## Лицензия

MIT
