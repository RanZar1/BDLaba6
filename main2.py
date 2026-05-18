import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter

# Настройка темы CustomTkinter
customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")


# ==========================================
# УРОВЕНЬ ВЗАИМОДЕЙСТВИЯ С БД (Data Access)
# ==========================================
class CafeDatabase:
    def __init__(self, db_name="cafe.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS jobtitle (
                JobTitleID INTEGER PRIMARY KEY AUTOINCREMENT,
                Title VARCHAR(50),
                Salary INT
            );
            CREATE TABLE IF NOT EXISTS place (
                PlaceID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name VARCHAR(50),
                Adress TEXT
            );
            CREATE TABLE IF NOT EXISTS stock (
                StockID INTEGER PRIMARY KEY AUTOINCREMENT,
                Adress TEXT,
                HowMany INT
            );
            CREATE TABLE IF NOT EXISTS client (
                ClientID INTEGER PRIMARY KEY AUTOINCREMENT,
                NameC VARCHAR(50),
                TableNumber INT
            );
            CREATE TABLE IF NOT EXISTS menu (
                MenuID INTEGER PRIMARY KEY AUTOINCREMENT,
                BranchID INT REFERENCES place(PlaceID),
                Category VARCHAR(50),
                Size VARCHAR(20)
            );
            CREATE TABLE IF NOT EXISTS person (
                PersonID INTEGER PRIMARY KEY AUTOINCREMENT,
                FIO VARCHAR(100),
                PhoneN VARCHAR(20),
                Adress TEXT,
                JobTitleID INT REFERENCES jobtitle(JobTitleID),
                BranchID INT REFERENCES place(PlaceID)
            );
            CREATE TABLE IF NOT EXISTS product (
                ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
                StockID INT REFERENCES stock(StockID),
                NameP VARCHAR(100),
                Quantity INT,
                BBD DATE
            );
            CREATE TABLE IF NOT EXISTS dish (
                dishID INTEGER PRIMARY KEY AUTOINCREMENT,
                MenuID INT REFERENCES menu(MenuID),
                NameD VARCHAR(100),
                weight INT,
                Price INT,
                BJU VARCHAR(50)
            );
            CREATE TABLE IF NOT EXISTS supply (
                SupplyID INTEGER PRIMARY KEY AUTOINCREMENT,
                ProductID INT REFERENCES product(ProductID),
                ProvideName VARCHAR(100),
                Kol_vo INT
            );
            CREATE TABLE IF NOT EXISTS "order" (
                OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
                ClientID INT REFERENCES client(ClientID),
                PersonID INT REFERENCES person(PersonID),
                Summ INT,
                Time TIMESTAMP,
                NumberOf INT
            );
            CREATE TABLE IF NOT EXISTS "Recipe" (
                dishID INT REFERENCES dish(dishID),
                ProductID INT REFERENCES product(ProductID),
                WeightP INT,
                PRIMARY KEY (dishID, ProductID)
            );
            CREATE TABLE IF NOT EXISTS order_item (
                OrderID INT REFERENCES "order"(OrderID),
                DishID INT REFERENCES dish(dishID),
                Quantity INT,
                PriceFix INT,
                PRIMARY KEY (OrderID, DishID)
            );
            CREATE TABLE IF NOT EXISTS promocode (
                PromoID INTEGER PRIMARY KEY AUTOINCREMENT,
                Code VARCHAR(20),
                Discount INT
);
        ''')

        self.cursor.execute("SELECT COUNT(*) FROM jobtitle")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executescript('''
                        -- ====================================================
                        -- 1. ДОЛЖНОСТИ И НАПРАВЛЕНИЯ
                        -- ====================================================
                        INSERT INTO jobtitle (Title, Salary) VALUES 
                        ('Член бригады ресторана', 38000), 
                        ('Инструктор по обучению', 45000), 
                        ('Менеджер смены', 55000), 
                        ('Директор предприятия', 90000), 
                        ('Специалист отдела кадров', 45000);

                        -- ====================================================
                        -- 2. ВОЛГОГРАДСКИЕ ФИЛИАЛЫ И СКЛАДЫ
                        -- ====================================================
                        INSERT INTO place (Name, Adress) VALUES 
                        ('Вкусно - и точка (Парк Хаус)', 'б-р 30-летия Победы, 21'), 
                        ('Вкусно - и точка (Акварель)', 'Университетский пр-т, 107'),
                        ('Вкусно - и точка (Центр)', 'Аллея Героев, 1'),
                        ('Вкусно - и точка (Ворошиловский)', 'ул. Рабоче-Крестьянская, 10');

                        INSERT INTO stock (Adress, HowMany) VALUES 
                        ('Локальный склад ПХ', 5000),
                        ('Локальный склад Акварель', 6000),
                        ('Волгоградский РаспредЦентр (ш. Авиаторов, 15)', 200000);

                        INSERT INTO client (NameC, TableNumber) VALUES 
                        ('Локатор 01', 1), ('Локатор 12', 12), ('На вынос', 0), ('Доставка (Яндекс)', 0);

                        -- ====================================================
                        -- 3. СОТРУДНИКИ
                        -- ====================================================
                        INSERT INTO person (FIO, PhoneN, Adress, JobTitleID, BranchID) VALUES 
                        ('Смирнов Илья Сергеевич', '89021112233', 'ул. 8-й Воздушной Армии, 35', 3, 1),
                        ('Волкова Анна Игоревна', '89042223344', 'пр-т им. Ленина, 53', 1, 1),
                        ('Петров Дмитрий Алексеевич', '89375556677', 'ул. Кирова, 120', 1, 2),
                        ('Козлов Максим Андреевич', '89170001122', 'ул. Мира, 10', 2, 1),
                        ('Соколова Елена Викторовна', '89608889900', 'ул. Еременко, 44', 4, 3);

                        -- ====================================================
                        -- 4. КАТЕГОРИИ МЕНЮ (Привязаны к Парк Хаусу для примера)
                        -- ====================================================
                        INSERT INTO menu (BranchID, Category, Size) VALUES 
                        (1, 'Бургеры', 'Стандарт'), 
                        (1, 'Стартеры и Картофель', 'Стандарт'), 
                        (1, 'Напитки', '0.4 л'), 
                        (1, 'Десерты и Выпечка', 'Стандарт');

                        -- ====================================================
                        -- 5. ТОВАРНЫЙ СКЛАД (Сырье для инвентаризации)
                        -- ====================================================
                        INSERT INTO product (StockID, NameP, Quantity, BBD) VALUES 
                        (3, 'Булочка регулярная (Гамбургер)', 2500, '2026-06-01'),
                        (3, 'Булочка Биг Хит (с кунжутом)', 1800, '2026-05-30'),
                        (3, 'Котлета говяжья 100% (малая)', 3500, '2026-06-15'),
                        (3, 'Котлета говяжья Гранд (крупная)', 42, '2026-05-24'), -- КРИТИЧЕСКИЙ ОСТАТОК!
                        (3, 'Филе минтая в панировке', 1200, '2026-07-10'),
                        (3, 'Чикен фри / Наггетсы (курица)', 20, '2026-06-20'),    -- КРИТИЧЕСКИЙ ОСТАТОК!
                        (3, 'Картофель фри (соломка замороженная)', 900, '2026-08-12'),
                        (3, 'Сыр Чеддер плавленый (ломтики)', 4000, '2026-09-01'),
                        (3, 'Сироп Добрый Кола', 150, '2026-11-30'),
                        (3, 'Смесь для Мороженого / Коктейлей', 8, '2026-05-22'),  -- КРИТИЧЕСКИЙ ОСТАТОК!
                        (3, 'Начинка Вишневая (для пирожков)', 600, '2026-07-05'),
                        (3, 'Соус Биг Хит фирменный', 850, '2026-06-18');

                        -- ====================================================
                        -- 6. КОНТРАГЕНТЫ ПОСТАВОК
                        -- ====================================================
                        INSERT INTO supply (ProductID, ProvideName, Kol_vo) VALUES 
                        (3, 'АПХ Мираторг', 5000),
                        (4, 'АПХ Мираторг', 2000),
                        (7, 'Лэм Уэстон Белая Дача', 1500),
                        (9, 'ООО Мултон Партнерс', 300),
                        (10, 'Эрманн Сибирь', 100);

                        -- ====================================================
                        -- 7. ГОТОВЫЕ БЛЮДА В МЕНЮ (С ценами и БЖУ)
                        -- ====================================================
                        -- Категория 1: Бургеры
                        INSERT INTO dish (MenuID, NameD, weight, Price, BJU) VALUES 
                        (1, 'Гамбургер', 100, 65, 'Б: 9г, Ж: 10г, У: 30г'),
                        (1, 'Чизбургер', 115, 78, 'Б: 12г, Ж: 14г, У: 32г'),
                        (1, 'Двойной Чизбургер', 170, 145, 'Б: 22г, Ж: 23г, У: 34г'),
                        (1, 'Биг Хит', 224, 185, 'Б: 27г, Ж: 25г, У: 41г'),
                        (1, 'Гранд', 200, 175, 'Б: 30г, Ж: 26г, У: 36г'),
                        (1, 'Чикен Бургер', 125, 62, 'Б: 11г, Ж: 12г, У: 35г'),
                        (1, 'Фиш Бургер', 135, 149, 'Б: 15г, Ж: 13г, У: 38г');

                        -- Категория 2: Стартеры и Картофель
                        INSERT INTO dish (MenuID, NameD, weight, Price, BJU) VALUES 
                        (2, 'Картофель Фри (Малый)', 70, 75, 'Б: 2г, Ж: 9г, У: 25г'),
                        (2, 'Картофель Фри (Средний)', 110, 95, 'Б: 4г, Ж: 15г, У: 40г'),
                        (2, 'Картофель Фри (Большой)', 150, 115, 'Б: 5г, Ж: 20г, У: 55г'),
                        (2, 'Картофель по-деревенски', 130, 99, 'Б: 3г, Ж: 11г, У: 32г'),
                        (2, 'Наггетсы (6 шт.)', 100, 89, 'Б: 14г, Ж: 10г, У: 18г'),
                        (2, 'Наггетсы (9 шт.)', 150, 119, 'Б: 21г, Ж: 15г, У: 27г'),
                        (2, 'Сырные Колечки (3 шт.)', 60, 99, 'Б: 8г, Ж: 12г, У: 15г');

                        -- Категория 3: Напитки
                        INSERT INTO dish (MenuID, NameD, weight, Price, BJU) VALUES 
                        (3, 'Добрый Кола 0.4', 400, 89, 'Б: 0г, Ж: 0г, У: 44г'),
                        (3, 'Добрый Кола 0.5', 500, 99, 'Б: 0г, Ж: 0г, У: 55г'),
                        (3, 'Добрый Апельсин 0.4', 400, 89, 'Б: 0г, Ж: 0г, У: 48г'),
                        (3, 'Капучино (Малый)', 200, 109, 'Б: 4г, Ж: 3г, У: 8г'),
                        (3, 'Латте (Средний)', 300, 149, 'Б: 6г, Ж: 5г, У: 12г'),
                        (3, 'Чай Черный', 300, 69, 'Б: 0г, Ж: 0г, У: 0г');

                        -- Категория 4: Десерты и Выпечка
                        INSERT INTO dish (MenuID, NameD, weight, Price, BJU) VALUES 
                        (4, 'Пирожок Вишня', 80, 79, 'Б: 3г, Ж: 8г, У: 34г'),
                        (4, 'Пирожок Клубника-Малина', 80, 79, 'Б: 3г, Ж: 8г, У: 35г'),
                        (4, 'Мороженое Карамельное', 145, 109, 'Б: 4г, Ж: 6г, У: 42г'),
                        (4, 'Мороженое Шоколадное', 145, 109, 'Б: 4г, Ж: 7г, У: 41г'),
                        (4, 'Яблочный Пирог', 100, 125, 'Б: 2г, Ж: 11г, У: 38г');
                        
                        INSERT INTO promocode (Code, Discount) VALUES ('MINUS10', 10), ('STUDENT', 15);

-- ====================================================
                        -- 8. СТАТИСТИКА ЗАКАЗОВ (Чеки для аналитики)
                        -- ====================================================
                        -- Чек 1
                        INSERT INTO "order" (ClientID, PersonID, Summ, Time, NumberOf) VALUES (1, 2, 36900, '2026-05-18 11:00:00', 10);
                        INSERT INTO order_item (OrderID, DishID, Quantity, PriceFix) VALUES (1, 4, 100, 185), (1, 9, 100, 95), (1, 16, 100, 89);

                        -- Чек 2 (Плотный обед, Биг Хиты, картошка)
                        INSERT INTO "order" (ClientID, PersonID, Summ, Time, NumberOf) VALUES (2, 2, 84000, '2026-05-18 12:30:00', 11);
                        INSERT INTO order_item (OrderID, DishID, Quantity, PriceFix) VALUES (2, 4, 300, 185), (2, 9, 300, 95);

                        -- Чек 3 (Много Двойных чизбургеров и наггетсов)
                        INSERT INTO "order" (ClientID, PersonID, Summ, Time, NumberOf) VALUES (3, 3, 76600, '2026-05-18 13:15:00', 12);
                        INSERT INTO order_item (OrderID, DishID, Quantity, PriceFix) VALUES (3, 3, 400, 145), (3, 13, 100, 119), (3, 15, 100, 67);

                        -- Чек 4 (Студенческий перекус: Гамбургеры и Кола)
                        INSERT INTO "order" (ClientID, PersonID, Summ, Time, NumberOf) VALUES (1, 3, 42400, '2026-05-18 14:05:00', 13);
                        INSERT INTO order_item (OrderID, DishID, Quantity, PriceFix) VALUES (4, 1, 500, 65), (4, 15, 100, 89);

                        -- Чек 5 (Только кофе и десерты)
                        INSERT INTO "order" (ClientID, PersonID, Summ, Time, NumberOf) VALUES (4, 1, 51500, '2026-05-18 15:00:00', 14);
                        INSERT INTO order_item (OrderID, DishID, Quantity, PriceFix) VALUES (5, 18, 200, 149), (5, 21, 200, 79), (5, 23, 100, 109);
                    ''')
        self.conn.commit()
    def get_persons(self):
        query = '''
            SELECT p.PersonID, p.FIO, p.PhoneN, p.Adress, j.Title, pl.Name 
            FROM person p
            JOIN jobtitle j ON p.JobTitleID = j.JobTitleID
            JOIN place pl ON p.BranchID = pl.PlaceID
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_jobtitles(self):
        self.cursor.execute("SELECT * FROM jobtitle")
        return self.cursor.fetchall()

    def get_places(self):
        self.cursor.execute("SELECT * FROM place")
        return self.cursor.fetchall()

    # НОВЫЙ МЕТОД: Получение уникальных категорий для выпадающего списка
    def get_categories(self):
        self.cursor.execute("SELECT DISTINCT Category FROM menu")
        # Возвращаем плоский список строк вместо списка кортежей
        return [row[0] for row in self.cursor.fetchall()]

    def add_person(self, fio, phone, address, job_id, branch_id):
        self.cursor.execute(
            "INSERT INTO person (FIO, PhoneN, Adress, JobTitleID, BranchID) VALUES (?, ?, ?, ?, ?)",
            (fio, phone, address, job_id, branch_id)
        )
        self.conn.commit()

    def update_person_phone(self, person_id, new_phone):
        self.cursor.execute("UPDATE person SET PhoneN = ? WHERE PersonID = ?", (new_phone, person_id))
        self.conn.commit()

    def delete_person(self, person_id):
        self.cursor.execute("DELETE FROM person WHERE PersonID = ?", (person_id,))
        self.conn.commit()

    def analytics_sales_by_category(self, category_exact):
        query = '''
            SELECT d.NameD, m.Category, SUM(oi.Quantity), SUM(oi.Quantity * oi.PriceFix)
            FROM dish d
            JOIN order_item oi ON d.dishID = oi.DishID
            JOIN menu m ON d.MenuID = m.MenuID
            WHERE m.Category = ?
            GROUP BY d.NameD, m.Category
            ORDER BY SUM(oi.Quantity * oi.PriceFix) DESC
        '''
        self.cursor.execute(query, (category_exact,))
        return self.cursor.fetchall()

    def analytics_low_stock(self, threshold):
        query = '''
            SELECT p.NameP, p.Quantity, s.Adress, COALESCE(sp.ProvideName, 'Неизвестен')
            FROM product p
            JOIN stock s ON p.StockID = s.StockID
            LEFT JOIN supply sp ON p.ProductID = sp.ProductID
            WHERE p.Quantity <= ?
            ORDER BY p.Quantity ASC
        '''
        self.cursor.execute(query, (threshold,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

    def get_promos(self):
        self.cursor.execute("SELECT * FROM promocode")
        return self.cursor.fetchall()

    def add_promo(self, code, discount):
        self.cursor.execute("INSERT INTO promocode (Code, Discount) VALUES (?, ?)", (code, discount))
        self.conn.commit()

    def update_promo(self, promo_id, new_discount):
        self.cursor.execute("UPDATE promocode SET Discount = ? WHERE PromoID = ?", (new_discount, promo_id))
        self.conn.commit()

    def delete_promo(self, promo_id):
        self.cursor.execute("DELETE FROM promocode WHERE PromoID = ?", (promo_id,))
        self.conn.commit()

    def add_dish_to_order(self, order_id, dish_id, quantity, price_fix):
        self.cursor.execute(
            "INSERT INTO order_item (OrderID, DishID, Quantity, PriceFix) VALUES (?, ?, ?, ?)",
            (order_id, dish_id, quantity, price_fix)
        )
        self.conn.commit()

    def remove_dish_from_order(self, order_id, dish_id):
        self.cursor.execute(
            "DELETE FROM order_item WHERE OrderID = ? AND DishID = ?",
            (order_id, dish_id)
        )
        self.conn.commit()

    def get_order_details(self, order_id):
        self.cursor.execute('''
            SELECT d.NameD, oi.Quantity, oi.PriceFix 
            FROM order_item oi
            JOIN dish d ON oi.DishID = d.dishID
            WHERE oi.OrderID = ?
        ''', (order_id,))
        return self.cursor.fetchall()

    def get_orders_list(self):
        self.cursor.execute("SELECT OrderID FROM \"order\"")
        return [str(row[0]) for row in self.cursor.fetchall()]

    def get_dishes_list(self):
        self.cursor.execute("SELECT dishID, NameD, Price FROM dish")
        return self.cursor.fetchall()

    def analytics_top_employees(self):
        query = '''
            SELECT p.FIO, COUNT(o.OrderID), SUM(o.Summ)
            FROM person p
            JOIN "order" o ON p.PersonID = o.PersonID
            GROUP BY p.FIO
            ORDER BY SUM(o.Summ) DESC
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

# ==========================================
# УРОВЕНЬ ИНТЕРФЕЙСА (Presentation Layer - GUI)
# ==========================================
class CafeApp:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("Управление рестораном | Вкусно - и точка")
        self.root.geometry("950x550")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#FFFFFF", foreground="#333333",
                        rowheight=30, fieldbackground="#FFFFFF", borderwidth=0)
        style.map('Treeview', background=[('selected', '#3B8ED0')])
        style.configure("Treeview.Heading",
                        background="#F0F0F0", foreground="#333333",
                        font=('Helvetica', 10, 'bold'), borderwidth=0, padding=5)

        self.tabview = customtkinter.CTkTabview(self.root, width=900, height=500)
        self.tabview.pack(fill='both', expand=True, padx=15, pady=15)

        self.tabview.add("Сотрудники (CRUD)")
        self.tabview.add("Промокоды (CRUD)")
        self.tabview.add("Редактор заказов (М:М)")
        self.tabview.add("Бизнес-Аналитика")


        self.setup_employees_tab()
        self.setup_promo_tab()
        self.setup_order_editor_tab()
        self.setup_analytics_tab()



    def setup_employees_tab(self):
        tab = self.tabview.tab("Сотрудники (CRUD)")

        control_frame = customtkinter.CTkFrame(tab, fg_color="transparent")
        control_frame.pack(side='top', fill='x', pady=(0, 10))

        customtkinter.CTkButton(control_frame, text="🔄 Обновить", width=120, command=self.load_employees).pack(
            side='left', padx=5)
        customtkinter.CTkButton(control_frame, text="➕ Добавить", width=120, command=self.add_employee_window).pack(
            side='left', padx=5)
        customtkinter.CTkButton(control_frame, text="✏️ Изменить телефон", width=150, command=self.edit_phone).pack(
            side='left', padx=5)
        customtkinter.CTkButton(control_frame, text="❌ Уволить", width=120, fg_color="#D84B4B", hover_color="#B53939",
                                command=self.delete_employee).pack(side='left', padx=5)

        tree_frame = customtkinter.CTkFrame(tab)
        tree_frame.pack(fill='both', expand=True)

        columns = ("id", "fio", "phone", "address", "job", "branch")
        self.tree_emp = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_emp.heading("id", text="ID")
        self.tree_emp.heading("fio", text="ФИО")
        self.tree_emp.heading("phone", text="Телефон")
        self.tree_emp.heading("address", text="Адрес")
        self.tree_emp.heading("job", text="Должность")
        self.tree_emp.heading("branch", text="Филиал")

        self.tree_emp.column("id", width=40, anchor='center')
        self.tree_emp.column("fio", width=220)
        self.tree_emp.column("phone", width=130, anchor='center')
        self.tree_emp.column("address", width=150)
        self.tree_emp.column("job", width=160)
        self.tree_emp.column("branch", width=200)

        self.tree_emp.pack(fill='both', expand=True, padx=2, pady=2)
        self.load_employees()

    def load_employees(self):
        for item in self.tree_emp.get_children():
            self.tree_emp.delete(item)
        for row in self.db.get_persons():
            self.tree_emp.insert("", tk.END, values=row)

    def add_employee_window(self):
        win = customtkinter.CTkToplevel(self.root)
        win.title("Новый сотрудник")
        win.geometry("400x380")
        win.attributes('-topmost', True)

        customtkinter.CTkLabel(win, text="Регистрация сотрудника", font=("Helvetica", 16, "bold")).pack(pady=10)

        entry_fio = customtkinter.CTkEntry(win, width=300, placeholder_text="ФИО")
        entry_fio.pack(pady=5)

        entry_phone = customtkinter.CTkEntry(win, width=300, placeholder_text="Телефон (например, 8900...)")
        entry_phone.pack(pady=5)

        entry_address = customtkinter.CTkEntry(win, width=300, placeholder_text="Адрес проживания")
        entry_address.pack(pady=5)

        jobs = self.db.get_jobtitles()
        job_combo = customtkinter.CTkComboBox(win, values=[f"{j[0]} - {j[1]}" for j in jobs], width=300)
        job_combo.set("Выберите должность...")
        job_combo.pack(pady=5)

        places = self.db.get_places()
        place_combo = customtkinter.CTkComboBox(win, values=[f"{p[0]} - {p[1]}" for p in places], width=300)
        place_combo.set("Выберите филиал...")
        place_combo.pack(pady=5)

        def save():
            try:
                fio = entry_fio.get()
                phone = entry_phone.get()
                address = entry_address.get()
                job_id = int(job_combo.get().split(" - ")[0])
                branch_id = int(place_combo.get().split(" - ")[0])

                if not all([fio, phone, address]):
                    raise ValueError

                self.db.add_person(fio, phone, address, job_id, branch_id)
                self.load_employees()
                win.destroy()
                messagebox.showinfo("Успех", "Сотрудник успешно добавлен в базу.")
            except:
                messagebox.showerror("Ошибка", "Заполните все поля и выберите значения из списков.")

        customtkinter.CTkButton(win, text="Сохранить в БД", command=save, width=300).pack(pady=20)

    def edit_phone(self):
        selected = self.tree_emp.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите сотрудника в таблице!")
            return

        person_id = self.tree_emp.item(selected[0])['values'][0]

        dialog = customtkinter.CTkInputDialog(text="Введите новый номер телефона:", title="Смена номера")
        new_phone = dialog.get_input()
        if new_phone:
            self.db.update_person_phone(person_id, new_phone)
            self.load_employees()

    def delete_employee(self):
        selected = self.tree_emp.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите сотрудника в таблице!")
            return

        person_id = self.tree_emp.item(selected[0])['values'][0]
        fio = self.tree_emp.item(selected[0])['values'][1]

        if messagebox.askyesno("Подтверждение", f"Оформить увольнение сотрудника: {fio}?"):
            self.db.delete_person(person_id)
            self.load_employees()

    def setup_promo_tab(self):
        # Получаем созданную вкладку
        tab = self.tabview.tab("Промокоды (CRUD)")

        # Фрейм для кнопок управления
        control_frame = customtkinter.CTkFrame(tab, fg_color="transparent")
        control_frame.pack(side='top', fill='x', pady=(0, 10))

        customtkinter.CTkButton(control_frame, text="🔄 Обновить", width=100,
                                command=self.load_promos).pack(side='left', padx=5)
        customtkinter.CTkButton(control_frame, text="➕ Добавить", width=120,
                                command=self.add_promo_window).pack(side='left', padx=5)
        customtkinter.CTkButton(control_frame, text="✏️ Изменить скидку", width=150,
                                command=self.edit_promo_discount).pack(side='left', padx=5)
        customtkinter.CTkButton(control_frame, text="❌ Удалить", width=100, fg_color="#D84B4B",
                                hover_color="#B53939", command=self.delete_promo).pack(side='left', padx=5)

        # Фрейм для таблицы
        tree_frame = customtkinter.CTkFrame(tab)
        tree_frame.pack(fill='both', expand=True)

        # Настройка таблицы
        columns = ("id", "code", "discount")
        self.tree_promo = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_promo.heading("id", text="ID")
        self.tree_promo.heading("code", text="Промокод")
        self.tree_promo.heading("discount", text="Скидка (%)")

        self.tree_promo.column("id", width=50, anchor='center')
        self.tree_promo.column("code", width=250, anchor='center')
        self.tree_promo.column("discount", width=150, anchor='center')

        self.tree_promo.pack(fill='both', expand=True, padx=2, pady=2)

        # Загружаем данные при старте
        self.load_promos()

    # --- МЕТОДЫ ДЛЯ РАБОТЫ КНОПОК ПРОМОКОДОВ ---

    def load_promos(self):
        # Очистка старых данных
        for item in self.tree_promo.get_children():
            self.tree_promo.delete(item)
        # Загрузка новых
        for row in self.db.get_promos():
            self.tree_promo.insert("", tk.END, values=row)

    def add_promo_window(self):
        win = customtkinter.CTkToplevel(self.root)
        win.title("Новый промокод")
        win.geometry("300x250")
        win.attributes('-topmost', True)  # Окно поверх остальных

        customtkinter.CTkLabel(win, text="Добавление промокода", font=("Helvetica", 14, "bold")).pack(pady=10)

        entry_code = customtkinter.CTkEntry(win, width=200, placeholder_text="Код (например, NEW20)")
        entry_code.pack(pady=5)

        entry_discount = customtkinter.CTkEntry(win, width=200, placeholder_text="Скидка (только число)")
        entry_discount.pack(pady=5)

        def save():
            code = entry_code.get()
            discount = entry_discount.get()

            # Проверка, что скидка введена цифрами
            if not code or not discount.isdigit():
                messagebox.showerror("Ошибка", "Введите код и числовое значение скидки.")
                return

            self.db.add_promo(code, int(discount))
            self.load_promos()  # Обновляем таблицу
            win.destroy()  # Закрываем окно
            messagebox.showinfo("Успех", "Промокод успешно добавлен.")

        customtkinter.CTkButton(win, text="Сохранить", command=save, width=200).pack(pady=20)

    def edit_promo_discount(self):
        selected = self.tree_promo.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Сначала выберите промокод в таблице!")
            return

        promo_id = self.tree_promo.item(selected[0])['values'][0]

        # Запрос новой скидки через диалог
        dialog = customtkinter.CTkInputDialog(text="Введите новый размер скидки (%):", title="Изменение скидки")
        new_discount = dialog.get_input()

        if new_discount and new_discount.isdigit():
            self.db.update_promo(promo_id, int(new_discount))
            self.load_promos()
        elif new_discount:  # Если ввели буквы вместо цифр
            messagebox.showerror("Ошибка", "Скидка должна быть целым числом!")

    def delete_promo(self):
        selected = self.tree_promo.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Сначала выберите промокод в таблице!")
            return

        promo_id = self.tree_promo.item(selected[0])['values'][0]
        code = self.tree_promo.item(selected[0])['values'][1]

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить промокод '{code}'?"):
            self.db.delete_promo(promo_id)
            self.load_promos()

    def setup_analytics_tab(self):
        tab = self.tabview.tab("Бизнес-Аналитика")

        # --- Блок 1: Анализ продаж (С выпадающим списком) ---
        f1 = customtkinter.CTkFrame(tab)
        f1.pack(fill='x', padx=5, pady=5)

        customtkinter.CTkLabel(f1, text="1. Отчет по продажам (Топ блюд):", font=("Helvetica", 13, "bold")).pack(
            side='left', padx=10, pady=10)

        # Получаем категории из БД и создаем ComboBox
        categories = self.db.get_categories()
        if not categories:
            categories = ["Нет категорий"]

        self.category_combo = customtkinter.CTkComboBox(f1, values=categories, width=200, state="readonly")
        self.category_combo.set(categories[0])  # Ставим первую категорию по умолчанию
        self.category_combo.pack(side='left', padx=10, pady=10)

        customtkinter.CTkButton(f1, text="Сформировать", command=self.run_analytics_1).pack(side='left', padx=10,
                                                                                            pady=10)

        # --- Блок 2: Склад ---
        f2 = customtkinter.CTkFrame(tab)
        f2.pack(fill='x', padx=5, pady=5)

        customtkinter.CTkLabel(f2, text="2. Инвентаризация (Остаток меньше чем):", font=("Helvetica", 13, "bold")).pack(
            side='left', padx=10, pady=10)
        self.entry_stock_search = customtkinter.CTkEntry(f2, placeholder_text="Мин. количество шт.", width=160)
        self.entry_stock_search.pack(side='left', padx=10, pady=10)
        customtkinter.CTkButton(f2, text="Проверить склад", command=self.run_analytics_2).pack(side='left', padx=10,
                                                                                               pady=10)

        # --- Блок 3: ТОП сотрудников ---
        f3 = customtkinter.CTkFrame(tab)
        f3.pack(fill='x', padx=5, pady=5)

        customtkinter.CTkLabel(f3, text="3. Эффективность (ТОП сотрудников по выручке):",
                               font=("Helvetica", 13, "bold")).pack(side='left', padx=10, pady=10)
        customtkinter.CTkButton(f3, text="Сформировать ТОП", command=self.run_analytics_3).pack(side='left', padx=10,
                                                                                                pady=10)
        # --- Таблица результатов ---
        res_frame = customtkinter.CTkFrame(tab)
        res_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree_analytics = ttk.Treeview(res_frame, columns=("c1", "c2", "c3", "c4"), show="headings")
        self.tree_analytics.pack(fill='both', expand=True, padx=2, pady=2)

    def run_analytics_1(self):
        cat_exact = self.category_combo.get()
        if cat_exact == "Нет категорий":
            return

        res = self.db.analytics_sales_by_category(cat_exact)

        self.tree_analytics.heading("c1", text="Блюдо")
        self.tree_analytics.heading("c2", text="Категория")
        self.tree_analytics.heading("c3", text="Продано (шт.)")
        self.tree_analytics.heading("c4", text="Выручка (руб.)")

        self.tree_analytics.column("c1", width=200)
        self.tree_analytics.column("c2", width=150)
        self.tree_analytics.column("c3", width=100, anchor='center')
        self.tree_analytics.column("c4", width=100, anchor='center')

        self.tree_analytics.delete(*self.tree_analytics.get_children())
        for r in res:
            self.tree_analytics.insert("", tk.END, values=r)

    def run_analytics_2(self):
        try:
            threshold = int(self.entry_stock_search.get())
            res = self.db.analytics_low_stock(threshold)

            self.tree_analytics.heading("c1", text="Сырье (Продукт)")
            self.tree_analytics.heading("c2", text="Остаток (шт/упак)")
            self.tree_analytics.heading("c3", text="Адрес хранения")
            self.tree_analytics.heading("c4", text="Контрагент (Поставщик)")

            self.tree_analytics.column("c1", width=200)
            self.tree_analytics.column("c2", width=100, anchor='center')
            self.tree_analytics.column("c3", width=250)
            self.tree_analytics.column("c4", width=200)

            self.tree_analytics.delete(*self.tree_analytics.get_children())
            for r in res:
                self.tree_analytics.insert("", tk.END, values=r)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Укажите число для проверки остатков (например, 50).")

    def setup_order_editor_tab(self):
        tab = self.tabview.tab("Редактор заказов (М:М)")

        # Фрейм управления
        ctrl_frame = customtkinter.CTkFrame(tab, fg_color="transparent")
        ctrl_frame.pack(side='top', fill='x', pady=(0, 10))

        # Выпадающий список заказов
        customtkinter.CTkLabel(ctrl_frame, text="Заказ №:").pack(side='left', padx=5)
        orders = self.db.get_orders_list()
        self.combo_order = customtkinter.CTkComboBox(ctrl_frame, values=orders if orders else ["Нет заказов"], width=80,
                                                     command=self.load_order_details)
        self.combo_order.pack(side='left', padx=5)

        # Выпадающий список блюд
        customtkinter.CTkLabel(ctrl_frame, text="Блюдо:").pack(side='left', padx=(15, 5))
        self.dishes_data = self.db.get_dishes_list()
        dish_values = [f"{d[0]} - {d[1]} ({d[2]} руб.)" for d in self.dishes_data]
        self.combo_dish = customtkinter.CTkComboBox(ctrl_frame, values=dish_values if dish_values else ["Нет блюд"],
                                                    width=250)
        self.combo_dish.pack(side='left', padx=5)

        # Поле количества
        self.entry_qty = customtkinter.CTkEntry(ctrl_frame, placeholder_text="Кол-во", width=60)
        self.entry_qty.pack(side='left', padx=5)

        # Кнопки
        customtkinter.CTkButton(ctrl_frame, text="➕ Добавить в чек", width=120, command=self.add_dish_to_receipt).pack(
            side='left', padx=5)
        customtkinter.CTkButton(ctrl_frame, text="❌ Удалить из чека", width=120, fg_color="#D84B4B",
                                hover_color="#B53939", command=self.remove_dish_from_receipt).pack(side='left', padx=5)

        # Таблица состава заказа
        tree_frame = customtkinter.CTkFrame(tab)
        tree_frame.pack(fill='both', expand=True)

        self.tree_order = ttk.Treeview(tree_frame, columns=("dish", "qty", "price"), show="headings",
                                       selectmode="browse")
        self.tree_order.heading("dish", text="Наименование блюда")
        self.tree_order.heading("qty", text="Кол-во")
        self.tree_order.heading("price", text="Цена фикс.")

        self.tree_order.column("dish", width=300)
        self.tree_order.column("qty", width=100, anchor='center')
        self.tree_order.column("price", width=100, anchor='center')
        self.tree_order.pack(fill='both', expand=True, padx=2, pady=2)

        # Загружаем состав первого заказа при старте
        if orders:
            self.combo_order.set(orders[0])
            self.load_order_details(orders[0])

    def load_order_details(self, choice=None):
        order_id = self.combo_order.get()
        if order_id == "Нет заказов": return

        # Очистка таблицы
        for item in self.tree_order.get_children():
            self.tree_order.delete(item)

        # Загрузка новых данных
        for row in self.db.get_order_details(int(order_id)):
            self.tree_order.insert("", tk.END, values=row)

    def add_dish_to_receipt(self):
        order_id = self.combo_order.get()
        dish_str = self.combo_dish.get()
        qty = self.entry_qty.get()

        if not qty.isdigit():
            messagebox.showerror("Ошибка", "Укажите количество числом!")
            return

        dish_id = int(dish_str.split(" - ")[0])
        # Находим цену выбранного блюда
        price_fix = next(d[2] for d in self.dishes_data if d[0] == dish_id)

        try:
            self.db.add_dish_to_order(int(order_id), dish_id, int(qty), price_fix)
            self.load_order_details()  # Обновляем таблицу
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка",
                                 "Это блюдо уже есть в чеке! Удалите его и добавьте заново с нужным количеством.")

    def remove_dish_from_receipt(self):
        selected = self.tree_order.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите блюдо в таблице для удаления!")
            return

        order_id = int(self.combo_order.get())
        dish_name = self.tree_order.item(selected[0])['values'][0]

        # Ищем ID блюда по имени
        dish_id = next((d[0] for d in self.dishes_data if d[1] == dish_name), None)

        if dish_id and messagebox.askyesno("Удаление", f"Удалить '{dish_name}' из заказа?"):
            self.db.remove_dish_from_order(order_id, dish_id)
            self.load_order_details()

    def run_analytics_3(self):
        res = self.db.analytics_top_employees()

        self.tree_analytics.heading("c1", text="Сотрудник (ФИО)")
        self.tree_analytics.heading("c2", text="Кол-во чеков")
        self.tree_analytics.heading("c3", text="Принесенная выручка (руб.)")
        self.tree_analytics.heading("c4", text="")  # Скрываем четвертую колонку

        self.tree_analytics.column("c1", width=250)
        self.tree_analytics.column("c2", width=120, anchor='center')
        self.tree_analytics.column("c3", width=180, anchor='center')
        self.tree_analytics.column("c4", width=0, stretch=False)

        self.tree_analytics.delete(*self.tree_analytics.get_children())
        for r in res:
            # Передаем пустое значение для 4-й колонки
            self.tree_analytics.insert("", tk.END, values=(r[0], r[1], r[2], ""))


if __name__ == "__main__":
    db = CafeDatabase()
    root = customtkinter.CTk()
    app = CafeApp(root, db)


    def on_closing():
        db.close()
        root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()