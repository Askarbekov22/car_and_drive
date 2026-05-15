import aiosqlite

DB_NAME = "auto_park.db"


async def add_column_if_not_exists(db, table_name, column_name, column_type):
    cursor = await db.execute(f"PRAGMA table_info({table_name})")
    columns = await cursor.fetchall()
    existing_columns = [column[1] for column in columns]

    if column_name not in existing_columns:
        await db.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        )


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await add_column_if_not_exists(db, "drivers", "passport_front", "TEXT")
        await add_column_if_not_exists(db, "drivers", "passport_back", "TEXT")
        await add_column_if_not_exists(db, "drivers", "address", "TEXT")
        await add_column_if_not_exists(db, "drivers", "extra_contact_1", "TEXT")
        await add_column_if_not_exists(db, "drivers", "extra_contact_2", "TEXT")
        await add_column_if_not_exists(db, "drivers", "hire_date", "TEXT")
        await add_column_if_not_exists(db, "drivers", "contract_file", "TEXT")
        await add_column_if_not_exists(db, "drivers", "deposit_amount", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "drivers", "deposit_receipt", "TEXT")
        await add_column_if_not_exists(db, "drivers", "deposit_limit", "REAL DEFAULT 20000")
        await add_column_if_not_exists(db, "drivers", "deposit_status", "TEXT DEFAULT 'active'")
        await add_column_if_not_exists(db, "drivers", "total_orders", "INTEGER DEFAULT 0")
        await add_column_if_not_exists(db, "drivers", "income_from_driver", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "drivers", "total_turnover", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "drivers", "damage_amount", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "drivers", "driver_salary_total", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "drivers", "debt", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "drivers", "fine_amount_total", "REAL DEFAULT 0")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL UNIQUE,
                model TEXT,
                status TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                car_id INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,

                orders_count INTEGER DEFAULT 0,
                turnover REAL DEFAULT 0,
                cash REAL DEFAULT 0,
                card REAL DEFAULT 0,

                fuel_expense REAL DEFAULT 0,
                yandex_commission REAL DEFAULT 0,

                driver_salary REAL DEFAULT 0,
                salary_percent REAL DEFAULT 0,
                recommended_salary REAL DEFAULT 0,

                fine_amount REAL DEFAULT 0,
                fine_reason TEXT,

                battery_percent INTEGER DEFAULT 0,

                start_front_photo TEXT,
                start_back_photo TEXT,
                start_left_photo TEXT,
                start_right_photo TEXT,

                front_photo TEXT,
                back_photo TEXT,
                left_photo TEXT,
                right_photo TEXT,
                charging_receipt TEXT,

                FOREIGN KEY(driver_id) REFERENCES drivers(id),
                FOREIGN KEY(car_id) REFERENCES cars(id)
            )
        """)

        await add_column_if_not_exists(db, "shifts", "driver_salary", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "shifts", "salary_percent", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "shifts", "recommended_salary", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "shifts", "fine_amount", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "shifts", "fine_reason", "TEXT")
        await add_column_if_not_exists(db, "shifts", "charging_receipt", "TEXT")
        await add_column_if_not_exists(db, "shifts", "start_front_photo", "TEXT")
        await add_column_if_not_exists(db, "shifts", "start_back_photo", "TEXT")
        await add_column_if_not_exists(db, "shifts", "start_left_photo", "TEXT")
        await add_column_if_not_exists(db, "shifts", "start_right_photo", "TEXT")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS accidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shift_id INTEGER NOT NULL,
                driver_id INTEGER,
                car_id INTEGER,
                accident_date TEXT,

                damage_amount REAL DEFAULT 0,
                payment_type TEXT,
                paid_amount REAL DEFAULT 0,
                debt_amount REAL DEFAULT 0,

                photo_1 TEXT,
                photo_2 TEXT,

                note TEXT,
                status TEXT DEFAULT 'open',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                closed_at TIMESTAMP,

                FOREIGN KEY(shift_id) REFERENCES shifts(id),
                FOREIGN KEY(driver_id) REFERENCES drivers(id),
                FOREIGN KEY(car_id) REFERENCES cars(id)
            )
        """)

        await add_column_if_not_exists(db, "accidents", "driver_id", "INTEGER")
        await add_column_if_not_exists(db, "accidents", "car_id", "INTEGER")
        await add_column_if_not_exists(db, "accidents", "accident_date", "TEXT")
        await add_column_if_not_exists(db, "accidents", "paid_amount", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "accidents", "debt_amount", "REAL DEFAULT 0")
        await add_column_if_not_exists(db, "accidents", "updated_at", "TIMESTAMP")
        await add_column_if_not_exists(db, "accidents", "closed_at", "TIMESTAMP")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS driver_fines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL,
                shift_id INTEGER,
                amount REAL DEFAULT 0,
                reason TEXT,
                deducted_amount REAL DEFAULT 0,
                remaining_debt REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(driver_id) REFERENCES drivers(id),
                FOREIGN KEY(shift_id) REFERENCES shifts(id)
            )
        """)

        await db.commit()