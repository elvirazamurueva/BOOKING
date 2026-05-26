"""
Графический интерфейс для системы бронирования столов в ресторане.
Использует tkinter с вкладками для различных операций.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from db_driver import PostgreSQLDatabase
from models.booking import Booking
from models.table import Table
from models.user import User


class BookingGUI:
    """Главное окно приложения с вкладками для различных операций."""

    def __init__(self, root):
        self.root = root
        self.root.title("Система бронирования столов в ресторане")
        self.root.geometry("900x600")

        # Подключение к базе данных
        self.db = PostgreSQLDatabase()
        self.db.connect()  # Подключаемся один раз при старте

        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Создаем вкладки
        self.create_users_tab()
        self.create_tables_tab()
        self.create_bookings_tab()
        self.create_status_tab()

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Обработчик закрытия окна."""
        if self.db.connection:
            self.db.close()
        self.root.destroy()

    # ==================== ВКЛАДКА ПОЛЬЗОВАТЕЛИ ====================

    def create_users_tab(self):
        """Создание вкладки для управления пользователями."""
        users_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(users_frame, text="Пользователи")

        # Фрейм для создания пользователя
        create_frame = ttk.LabelFrame(users_frame, text="Добавить пользователя", padding="10")
        create_frame.pack(fill="x", pady=(0, 10))

        # Поля для нового пользователя
        ttk.Label(create_frame, text="Имя пользователя:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.user_username = ttk.Entry(create_frame, width=30)
        self.user_username.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(create_frame, text="Email:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.user_email = ttk.Entry(create_frame, width=30)
        self.user_email.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(create_frame, text="Телефон:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.user_phone = ttk.Entry(create_frame, width=30)
        self.user_phone.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(create_frame, text="Имя:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.user_first_name = ttk.Entry(create_frame, width=30)
        self.user_first_name.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(create_frame, text="Фамилия:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.user_last_name = ttk.Entry(create_frame, width=30)
        self.user_last_name.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(create_frame, text="Добавить пользователя", command=self.add_user).grid(
            row=3, column=0, columnspan=4, pady=10
        )

        # Фрейм для поиска и отображения
        search_frame = ttk.Frame(users_frame)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Поиск по имени:").pack(side="left", padx=5)
        self.search_username = ttk.Entry(search_frame, width=20)
        self.search_username.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_user).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Показать всех", command=self.show_all_users).pack(side="left", padx=5)

        # Таблица пользователей
        columns = ("user_id", "username", "email", "phone", "first_name", "last_name", "is_active")
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.users_tree.heading(col, text=col.capitalize())
            self.users_tree.column(col, width=100)

        self.users_tree.column("user_id", width=60)
        self.users_tree.column("is_active", width=60)

        scrollbar = ttk.Scrollbar(users_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)

        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        btn_frame = ttk.Frame(users_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_frame, text="Обновить", command=self.show_all_users).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Выбрать пользователя", command=self.select_user).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_user).pack(side="left", padx=5)

        # Фрейм для обновления данных пользователя
        update_frame = ttk.LabelFrame(users_frame, text="Обновить данные пользователя", padding="10")
        update_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(update_frame, text="ID пользователя:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.update_user_id = ttk.Entry(update_frame, width=10)
        self.update_user_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(update_frame, text="Новое имя:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.update_username = ttk.Entry(update_frame, width=20)
        self.update_username.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(update_frame, text="Новый email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.update_email = ttk.Entry(update_frame, width=20)
        self.update_email.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(update_frame, text="Новый телефон:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.update_phone = ttk.Entry(update_frame, width=20)
        self.update_phone.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(update_frame, text="Обновить данные", command=self.update_user).grid(
            row=2, column=0, columnspan=4, pady=10
        )

        # Загрузка пользователей при старте
        self.show_all_users()

    def add_user(self):
        """Добавить нового пользователя."""
        username = self.user_username.get().strip()
        email = self.user_email.get().strip()
        phone = self.user_phone.get().strip() or None
        first_name = self.user_first_name.get().strip() or None
        last_name = self.user_last_name.get().strip() or None

        if not username or not email:
            messagebox.showerror("Ошибка", "Имя пользователя и Email обязательны!")
            return

        try:
            user_id = self.db.create_user(
                username=username,
                email=email,
                phone=phone,
                first_name=first_name,
                last_name=last_name
            )
            if user_id:
                messagebox.showinfo("Успех", f"Пользователь создан с ID: {user_id}")
                self.show_all_users()
                self.clear_user_fields()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать пользователя")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def clear_user_fields(self):
        """Очистить поля ввода пользователя."""
        self.user_username.delete(0, tk.END)
        self.user_email.delete(0, tk.END)
        self.user_phone.delete(0, tk.END)
        self.user_first_name.delete(0, tk.END)
        self.user_last_name.delete(0, tk.END)

    def show_all_users(self):
        """Показать всех пользователей."""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        try:
            users = self.db.get_all_users()
            for user in users:
                self.users_tree.insert("", "end", values=(
                    user.get("user_id", user.get("id")),
                    user.get("username", ""),
                    user.get("email", ""),
                    user.get("phone", ""),
                    user.get("first_name", ""),
                    user.get("last_name", ""),
                    user.get("is_active", True)
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def search_user(self):
        """Поиск пользователя по имени."""
        pattern = self.search_username.get().strip()
        if not pattern:
            messagebox.showwarning("Предупреждение", "Введите имя для поиска!")
            return

        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        try:
            users = self.db.search_users_by_username(pattern)
            for user in users:
                self.users_tree.insert("", "end", values=(
                    user.get("user_id", user.get("id")),
                    user.get("username", ""),
                    user.get("email", ""),
                    user.get("phone", ""),
                    user.get("first_name", ""),
                    user.get("last_name", ""),
                    user.get("is_active", True)
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def select_user(self):
        """Выбрать пользователя из таблицы."""
        selected = self.users_tree.selection()
        if selected:
            item = self.users_tree.item(selected[0])
            values = item["values"]
            user_id = values[0]
            self.update_user_id.delete(0, tk.END)
            self.update_user_id.insert(0, str(user_id))
            self.update_username.delete(0, tk.END)
            self.update_email.delete(0, tk.END)
            self.update_phone.delete(0, tk.END)
            messagebox.showinfo("Выбрано", f"Выбран пользователь с ID: {user_id}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из таблицы!")

    def update_user(self):
        """Обновить данные пользователя."""
        user_id_str = self.update_user_id.get().strip()
        new_username = self.update_username.get().strip() or None
        new_email = self.update_email.get().strip() or None
        new_phone = self.update_phone.get().strip() or None

        if not user_id_str:
            messagebox.showerror("Ошибка", "Введите ID пользователя!")
            return

        try:
            user_id = int(user_id_str)
        except ValueError:
            messagebox.showerror("Ошибка", "ID пользователя должен быть числом!")
            return

        if not new_username and not new_email and not new_phone:
            messagebox.showwarning("Предупреждение", "Введите новые данные для обновления!")
            return

        try:
            # Обновляем по отдельности
            if new_username:
                self.db.update_user(user_id, username=new_username)
            if new_email:
                self.db.update_user(user_id, email=new_email)
            if new_phone:
                self.db.update_user(user_id, phone=new_phone)
            messagebox.showinfo("Успех", "Данные пользователя обновлены!")
            self.show_all_users()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def delete_user(self):
        """Удалить пользователя."""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return

        item = self.users_tree.item(selected[0])
        user_id = item["values"][0]

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить пользователя с ID {user_id}?"):
            try:
                result = self.db.delete_user(user_id)
                if result:
                    messagebox.showinfo("Успех", "Пользователь удален!")
                    self.show_all_users()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить пользователя")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    # ==================== ВКЛАДКА СТОЛЫ ====================

    def create_tables_tab(self):
        """Создание вкладки для управления столами."""
        tables_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tables_frame, text="Столы")

        # Фрейм для создания стола
        create_frame = ttk.LabelFrame(tables_frame, text="Добавить стол", padding="10")
        create_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(create_frame, text="Номер стола:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.table_number = ttk.Entry(create_frame, width=15)
        self.table_number.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(create_frame, text="Количество мест:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.table_seats = ttk.Entry(create_frame, width=15)
        self.table_seats.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(create_frame, text="Расположение:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.table_location = ttk.Entry(create_frame, width=15)
        self.table_location.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(create_frame, text="Доступен:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.table_available = ttk.Checkbutton(create_frame)
        self.table_available.grid(row=1, column=3, padx=5, pady=5)
        self.table_available_var = tk.BooleanVar(value=True)
        self.table_available.config(variable=self.table_available_var)

        ttk.Button(create_frame, text="Добавить стол", command=self.add_table).grid(
            row=2, column=0, columnspan=4, pady=10
        )

        # Фрейм для поиска
        search_frame = ttk.Frame(tables_frame)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Фильтр по доступности:").pack(side="left", padx=5)
        self.table_filter_available = ttk.Checkbutton(search_frame, text="Только доступные")
        self.table_filter_available.pack(side="left", padx=5)
        self.table_filter_available_var = tk.BooleanVar(value=False)
        self.table_filter_available.config(variable=self.table_filter_available_var)
        self.table_filter_available.config(command=self.filter_tables)

        ttk.Button(search_frame, text="Показать все", command=self.show_all_tables).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Обновить", command=self.show_all_tables).pack(side="left", padx=5)

        # Таблица столов
        columns = ("table_id", "table_number", "seats", "location", "is_available")
        self.tables_tree = ttk.Treeview(tables_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tables_tree.heading(col, text=col.capitalize())
            self.tables_tree.column(col, width=120)

        self.tables_tree.column("table_id", width=60)
        self.tables_tree.column("is_available", width=80)

        scrollbar = ttk.Scrollbar(tables_frame, orient="vertical", command=self.tables_tree.yview)
        self.tables_tree.configure(yscrollcommand=scrollbar.set)

        self.tables_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        btn_frame = ttk.Frame(tables_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_frame, text="Изменить статус", command=self.toggle_table_status).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_table).pack(side="left", padx=5)

        # Загрузка столов при старте
        self.show_all_tables()

    def clear_table_fields(self):
        """Очистить поля ввода стола."""
        self.table_number.delete(0, tk.END)
        self.table_seats.delete(0, tk.END)
        self.table_location.delete(0, tk.END)
        self.table_available_var.set(True)

    def add_table(self):
        """Добавить новый стол."""
        try:
            table_number = int(self.table_number.get().strip())
            seats = int(self.table_seats.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Номер стола и количество мест должны быть числами!")
            return

        location = self.table_location.get().strip() or None
        is_available = self.table_available_var.get()

        try:
            # Вставляем в БД без table_id, чтобы SERIAL сгенерировал значение
            self.db.cursor.execute("""
                INSERT INTO restaurant_tables (table_number, seats, location, is_available)
                VALUES (%s, %s, %s, %s)
                RETURNING table_id;
            """, (table_number, seats, location, is_available))
            self.db.connection.commit()
            result = self.db.cursor.fetchone()
            new_id = result['table_id'] if result else None

            messagebox.showinfo("Успех", f"Стол #{table_number} добавлен с ID: {new_id}!")
            self.show_all_tables()
            self.clear_table_fields()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def show_all_tables(self):
        """Показать все столы."""
        for item in self.tables_tree.get_children():
            self.tables_tree.delete(item)

        try:
            tables = self.db.get_all_tables()
            
            for table in tables:
                self.tables_tree.insert("", "end", values=(
                    table.get("table_id"),
                    table.get("table_number"),
                    table.get("seats"),
                    table.get("location", ""),
                    "Да" if table.get("is_available") else "Нет"
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def filter_tables(self):
        """Показать только доступные столы (если чекбокс отмечен)."""
        for item in self.tables_tree.get_children():
            self.tables_tree.delete(item)

        try:
            if self.table_filter_available_var.get():
                tables = self.db.get_available_tables()
            else:
                tables = self.db.get_all_tables()
            
            for table in tables:
                self.tables_tree.insert("", "end", values=(
                    table.get("table_id"),
                    table.get("table_number"),
                    table.get("seats"),
                    table.get("location", ""),
                    "Да" if table.get("is_available") else "Нет"
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def toggle_table_status(self):
        """Изменить статус доступности стола на противоположный."""
        selected = self.tables_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите стол из таблицы!")
            return

        item = self.tables_tree.item(selected[0])
        table_id = item["values"][0]

        # Получаем текущий статус из БД
        try:
            table = self.db.get_table_by_id(table_id)
            if table:
                current_status = table.get("is_available", False)
                new_status = not current_status
                self.db.update_table_status(table_id, new_status)
                messagebox.showinfo("Успех", f"Статус стола изменен на {'доступен' if new_status else 'не доступен'}!")
                self.show_all_tables()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def delete_table(self):
        """Удалить стол."""
        selected = self.tables_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите стол для удаления!")
            return

        item = self.tables_tree.item(selected[0])
        table_id = item["values"][0]
        table_number = item["values"][1]

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить стол #{table_number}?"):
            try:
                result = self.db.delete_table(table_id)
                if result:
                    messagebox.showinfo("Успех", "Стол удален!")
                    self.show_all_tables()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    # ==================== ВКЛАДКА БРОНИРОВАНИЯ ====================

    def create_bookings_tab(self):
        """Создание вкладки для управления бронированиями."""
        bookings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(bookings_frame, text="Бронирования")

        # Фрейм для создания бронирования
        create_frame = ttk.LabelFrame(bookings_frame, text="Создать бронирование", padding="10")
        create_frame.pack(fill="x", pady=(0, 10))

        # Выбор пользователя
        ttk.Label(create_frame, text="Пользователь (ID):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.booking_user_id = ttk.Entry(create_frame, width=15)
        self.booking_user_id.grid(row=0, column=1, padx=5, pady=5)

        # Выбор стола
        ttk.Label(create_frame, text="Стол (ID):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.booking_table_id = ttk.Entry(create_frame, width=15)
        self.booking_table_id.grid(row=0, column=3, padx=5, pady=5)

        # Дата бронирования
        ttk.Label(create_frame, text="Дата бронирования:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.booking_date = ttk.Entry(create_frame, width=15)
        self.booking_date.grid(row=1, column=1, padx=5, pady=5)
        self.booking_date.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))

        # Длительность
        ttk.Label(create_frame, text="Длительность (мин):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.booking_duration = ttk.Entry(create_frame, width=15)
        self.booking_duration.grid(row=1, column=3, padx=5, pady=5)
        self.booking_duration.insert(0, "90")

        # Количество гостей
        ttk.Label(create_frame, text="Гостей:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.booking_guests = ttk.Entry(create_frame, width=15)
        self.booking_guests.grid(row=2, column=1, padx=5, pady=5)
        self.booking_guests.insert(0, "1")

        # Статус
        ttk.Label(create_frame, text="Статус:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.booking_status = ttk.Combobox(create_frame, width=13, values=["confirmed", "completed", "cancelled"])
        self.booking_status.grid(row=2, column=3, padx=5, pady=5)
        self.booking_status.set("confirmed")

        # Заметки
        ttk.Label(create_frame, text="Заметки:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.booking_notes = ttk.Entry(create_frame, width=30)
        self.booking_notes.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

        ttk.Button(create_frame, text="Создать бронирование", command=self.add_booking).grid(
            row=4, column=0, columnspan=4, pady=10
        )

        # Фрейм для фильтрации
        filter_frame = ttk.Frame(bookings_frame)
        filter_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filter_frame, text="Фильтр по статусу:").pack(side="left", padx=5)
        self.booking_filter_status = ttk.Combobox(filter_frame, width=15, values=["all", "confirmed", "completed", "cancelled"])
        self.booking_filter_status.pack(side="left", padx=5)
        self.booking_filter_status.set("all")

        ttk.Button(filter_frame, text="Применить", command=self.filter_bookings).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Показать все", command=self.show_all_bookings).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Обновить", command=self.show_all_bookings).pack(side="left", padx=5)

        # Таблица бронирований
        columns = ("booking_id", "user_id", "table_id", "booking_date", "duration_minutes", "guest_count", "status", "notes")
        self.bookings_tree = ttk.Treeview(bookings_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.bookings_tree.heading(col, text=col.replace("_", " ").capitalize())
            self.bookings_tree.column(col, width=100)

        self.bookings_tree.column("booking_id", width=60)
        self.bookings_tree.column("notes", width=150)

        scrollbar = ttk.Scrollbar(bookings_frame, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)

        self.bookings_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        btn_frame = ttk.Frame(bookings_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_frame, text="Выбрать бронирование", command=self.select_booking).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Изменить статус", command=self.change_booking_status).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отменить", command=self.cancel_booking).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_booking).pack(side="left", padx=5)

        # Загрузка бронирований при старте
        self.show_all_bookings()

    def add_booking(self):
        """Создать новое бронирование."""
        try:
            user_id = int(self.booking_user_id.get().strip())
            table_id = int(self.booking_table_id.get().strip())
            duration = int(self.booking_duration.get().strip())
            guests = int(self.booking_guests.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "ID пользователя, ID стола, длительность и количество гостей должны быть числами!")
            return

        try:
            booking_date = datetime.strptime(self.booking_date.get().strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте: YYYY-MM-DD HH:MM")
            return

        status = self.booking_status.get()
        notes = self.booking_notes.get().strip() or None

        try:
            # Проверяем существование пользователя
            users = self.db.search_users_by_username("")
            user_exists = any(u.get('user_id') == user_id for u in users)
            
            # Более надежная проверка - получаем всех пользователей и ищем по ID
            all_users = self.db.get_all_users()
            user_exists = any(u.get('user_id') == user_id for u in all_users)
            
            if not user_exists:
                messagebox.showerror(
                    "Ошибка",
                    f"Пользователь с ID {user_id} не найден!\n"
                    f"Пожалуйста, сначала создайте пользователя во вкладке 'Пользователи'."
                )
                return

            # Проверяем существование стола
            table = self.db.get_table_by_id(table_id)
            if not table:
                messagebox.showerror(
                    "Ошибка",
                    f"Стол с ID {table_id} не найден!\n"
                    f"Пожалуйста, сначала создайте стол во вкладке 'Столы'."
                )
                return

            # Проверяем конфликт бронирований
            conflict = self.db.check_booking_conflict(table_id, booking_date, duration)
            if conflict:
                conflict_date = conflict.get('booking_date')
                conflict_str = conflict_date.strftime("%Y-%m-%d %H:%M") if conflict_date else str(conflict_date)
                messagebox.showerror(
                    "Конфликт бронирования",
                    f"Стол #{table_id} уже забронирован на это время!\n"
                    f"Существующее бронирование: {conflict_str}\n"
                    f"Пожалуйста, выберите другое время."
                )
                return

            # Вставляем в БД без booking_id, чтобы SERIAL сгенерировал значение
            self.db.cursor.execute("""
                INSERT INTO bookings (user_id, table_id, booking_date, duration_minutes, guest_count, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING booking_id;
            """, (user_id, table_id, booking_date, duration, guests, status, notes))
            self.db.connection.commit()
            result = self.db.cursor.fetchone()
            new_id = result['booking_id'] if result else None

            messagebox.showinfo("Успех", f"Бронирование #{new_id} создано!")
            self.show_all_bookings()
            self.clear_booking_fields()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def clear_booking_fields(self):
        """Очистить поля ввода бронирования."""
        self.booking_user_id.delete(0, tk.END)
        self.booking_table_id.delete(0, tk.END)
        self.booking_date.delete(0, tk.END)
        self.booking_date.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.booking_duration.delete(0, tk.END)
        self.booking_duration.insert(0, "90")
        self.booking_guests.delete(0, tk.END)
        self.booking_guests.insert(0, "1")
        self.booking_status.set("confirmed")
        self.booking_notes.delete(0, tk.END)

    def select_booking(self):
        """Выбрать бронирование из таблицы."""
        selected = self.bookings_tree.selection()
        if selected:
            item = self.bookings_tree.item(selected[0])
            values = item["values"]
            booking_id = values[0]
            messagebox.showinfo("Выбрано", f"Выбрано бронирование с ID: {booking_id}")
        else:
            messagebox.showwarning("Предупреждение", "Выберите бронирование из таблицы!")

    def show_all_bookings(self):
        """Показать все бронирования."""
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        try:
            bookings = self.db.get_all_bookings()

            for booking in bookings:
                self.bookings_tree.insert("", "end", values=(
                    booking.get("booking_id"),
                    booking.get("user_id"),
                    booking.get("table_id"),
                    booking.get("booking_date"),
                    booking.get("duration_minutes"),
                    booking.get("guest_count"),
                    booking.get("status"),
                    booking.get("notes", "")
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def filter_bookings(self):
        """Отфильтровать бронирования по статусу."""
        status = self.booking_filter_status.get()

        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        try:
            if status == "all":
                bookings = self.db.get_all_bookings()
            else:
                bookings = self.db.get_bookings_by_status(status)

            for booking in bookings:
                self.bookings_tree.insert("", "end", values=(
                    booking.get("booking_id"),
                    booking.get("user_id"),
                    booking.get("table_id"),
                    booking.get("booking_date"),
                    booking.get("duration_minutes"),
                    booking.get("guest_count"),
                    booking.get("status"),
                    booking.get("notes", "")
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def change_booking_status(self):
        """Изменить статус бронирования."""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование из таблицы!")
            return

        item = self.bookings_tree.item(selected[0])
        booking_id = item["values"][0]

        new_status = simpledialog.askstring("Изменить статус",
                                            "Введите новый статус (confirmed/completed/cancelled):",
                                            initialvalue=item["values"][6])

        if new_status:
            try:
                self.db.update_booking_status(booking_id, new_status)
                messagebox.showinfo("Успех", f"Статус изменен на '{new_status}'!")
                self.show_all_bookings()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def cancel_booking(self):
        """Отменить бронирование."""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование из таблицы!")
            return

        item = self.bookings_tree.item(selected[0])
        booking_id = item["values"][0]

        if messagebox.askyesno("Подтверждение", "Отменить это бронирование?"):
            try:
                self.db.update_booking_status(booking_id, 'cancelled')
                messagebox.showinfo("Успех", "Бронирование отменено!")
                self.show_all_bookings()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def delete_booking(self):
        """Удалить бронирование."""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите бронирование для удаления!")
            return

        item = self.bookings_tree.item(selected[0])
        booking_id = item["values"][0]

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить бронирование #{booking_id}?"):
            try:
                result = self.db.delete_booking(booking_id)
                if result:
                    messagebox.showinfo("Успех", "Бронирование удалено!")
                    self.show_all_bookings()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    # ==================== ВКЛАДКА СТАТУС ====================

    def create_status_tab(self):
        """Создание вкладки для отображения статуса системы."""
        status_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(status_frame, text="Статус системы")

        # Информация о базе данных
        db_info_frame = ttk.LabelFrame(status_frame, text="Информация о базе данных", padding="10")
        db_info_frame.pack(fill="x", pady=(0, 10))

        self.db_info_text = tk.Text(db_info_frame, height=5, width=80)
        self.db_info_text.pack(fill="x")

        # Статистика
        stats_frame = ttk.LabelFrame(status_frame, text="Статистика", padding="10")
        stats_frame.pack(fill="both", expand=True)

        columns = ("metric", "value")
        self.stats_tree = ttk.Treeview(stats_frame, columns=columns, show="headings", height=10)
        self.stats_tree.heading("metric", text="Метрика")
        self.stats_tree.heading("value", text="Значение")
        self.stats_tree.column("metric", width=300)
        self.stats_tree.column("value", width=100)

        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)

        self.stats_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(status_frame, text="Обновить статистику", command=self.update_stats).pack(pady=10)

        # Обновление статуса при старте
        self.update_stats()

    def update_stats(self):
        """Обновить статистику системы."""
        # Обновление информации о БД
        self.db_info_text.delete(1.0, tk.END)
        
        if self.db.connection:
            self.db_info_text.insert(tk.END, "Подключение: Установлено\n")
            tables = self.db.get_table_names()
            self.db_info_text.insert(tk.END, f"Таблицы: {', '.join(tables) if tables else 'Нет таблиц'}\n")
        else:
            self.db_info_text.insert(tk.END, "Подключение: Не установлено\n")
            self.db_info_text.insert(tk.END, "Нажмите 'Обновить статистику' для проверки\n")

        # Обновление статистики
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        try:
            # Количество пользователей
            self.db.cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = self.db.cursor.fetchone()["count"]
            self.stats_tree.insert("", "end", values=("Всего пользователей", user_count))

            # Количество столов
            self.db.cursor.execute("SELECT COUNT(*) as count FROM restaurant_tables")
            table_count = self.db.cursor.fetchone()["count"]
            self.stats_tree.insert("", "end", values=("Всего столов", table_count))

            # Доступные столы
            self.db.cursor.execute("SELECT COUNT(*) as count FROM restaurant_tables WHERE is_available = true")
            available_count = self.db.cursor.fetchone()["count"]
            self.stats_tree.insert("", "end", values=("Доступных столов", available_count))

            # Количество бронирований
            self.db.cursor.execute("SELECT COUNT(*) as count FROM bookings")
            booking_count = self.db.cursor.fetchone()["count"]
            self.stats_tree.insert("", "end", values=("Всего бронирований", booking_count))

            # Активные бронирования
            self.db.cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'confirmed'")
            confirmed_count = self.db.cursor.fetchone()["count"]
            self.stats_tree.insert("", "end", values=("Активных бронирований", confirmed_count))

            # Отмененные бронирования
            self.db.cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'cancelled'")
            cancelled_count = self.db.cursor.fetchone()["count"]
            self.stats_tree.insert("", "end", values=("Отмененных бронирований", cancelled_count))
        except Exception as e:
            self.stats_tree.insert("", "end", values=("Ошибка", str(e)))


def main():
    """Запуск приложения."""
    root = tk.Tk()
    app = BookingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
