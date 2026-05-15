import aiosqlite

from database import DB_NAME


async def add_driver(
    full_name: str,
    phone: str,
    passport_front: str,
    passport_back: str,
    address: str,
    extra_contact_1: str,
    extra_contact_2: str,
    hire_date: str,
    contract_file: str,
    deposit_amount: float,
    deposit_receipt: str
):
    deposit_status = "stopped" if deposit_amount >= 20000 else "active"

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO drivers (
                full_name,
                phone,
                passport_front,
                passport_back,
                address,
                extra_contact_1,
                extra_contact_2,
                hire_date,
                contract_file,
                deposit_amount,
                deposit_receipt,
                deposit_limit,
                deposit_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name,
            phone,
            passport_front,
            passport_back,
            address,
            extra_contact_1,
            extra_contact_2,
            hire_date,
            contract_file,
            deposit_amount,
            deposit_receipt,
            20000,
            deposit_status
        ))

        await db.commit()


async def get_all_drivers():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT id, full_name
            FROM drivers
            ORDER BY full_name ASC
        """)

        return await cursor.fetchall()


async def get_all_drivers_full():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT 
                id,
                full_name,
                phone,
                deposit_amount,
                deposit_status,
                total_orders,
                income_from_driver,
                total_turnover,
                damage_amount,
                driver_salary_total,
                debt
            FROM drivers
            ORDER BY full_name ASC
        """)

        return await cursor.fetchall()


async def get_driver_by_id(driver_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT 
                id,
                full_name,
                phone,
                deposit_amount,
                deposit_status,
                total_orders,
                income_from_driver,
                total_turnover,
                damage_amount,
                driver_salary_total,
                debt
            FROM drivers
            WHERE id = ?
        """, (driver_id,))

        return await cursor.fetchone()


async def get_driver_by_full_name(full_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT 
                id,
                full_name,
                phone,
                deposit_amount,
                deposit_status,
                total_orders,
                income_from_driver,
                total_turnover,
                damage_amount,
                driver_salary_total,
                debt
            FROM drivers
            WHERE full_name = ?
        """, (full_name,))

        return await cursor.fetchone()


async def search_drivers(query: str):
    search_text = f"%{query}%"

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT 
                id,
                full_name,
                phone,
                deposit_amount,
                deposit_status,
                total_orders,
                income_from_driver,
                total_turnover,
                damage_amount,
                driver_salary_total,
                debt
            FROM drivers
            WHERE full_name LIKE ?
            OR phone LIKE ?
            ORDER BY full_name ASC
        """, (
            search_text,
            search_text
        ))

        return await cursor.fetchall()


async def filter_drivers(filter_type: str):
    async with aiosqlite.connect(DB_NAME) as db:
        if filter_type == "deposit_active":
            query = """
                SELECT 
                    id, full_name, phone, deposit_amount, deposit_status,
                    total_orders, income_from_driver, total_turnover,
                    damage_amount, driver_salary_total, debt
                FROM drivers
                WHERE deposit_status = 'active'
                ORDER BY full_name ASC
            """
            params = ()

        elif filter_type == "deposit_stopped":
            query = """
                SELECT 
                    id, full_name, phone, deposit_amount, deposit_status,
                    total_orders, income_from_driver, total_turnover,
                    damage_amount, driver_salary_total, debt
                FROM drivers
                WHERE deposit_status = 'stopped'
                ORDER BY full_name ASC
            """
            params = ()

        elif filter_type == "has_debt":
            query = """
                SELECT 
                    id, full_name, phone, deposit_amount, deposit_status,
                    total_orders, income_from_driver, total_turnover,
                    damage_amount, driver_salary_total, debt
                FROM drivers
                WHERE COALESCE(debt, 0) > 0
                ORDER BY debt DESC
            """
            params = ()

        elif filter_type == "no_debt":
            query = """
                SELECT 
                    id, full_name, phone, deposit_amount, deposit_status,
                    total_orders, income_from_driver, total_turnover,
                    damage_amount, driver_salary_total, debt
                FROM drivers
                WHERE COALESCE(debt, 0) = 0
                ORDER BY full_name ASC
            """
            params = ()

        elif filter_type == "has_damage":
            query = """
                SELECT 
                    id, full_name, phone, deposit_amount, deposit_status,
                    total_orders, income_from_driver, total_turnover,
                    damage_amount, driver_salary_total, debt
                FROM drivers
                WHERE COALESCE(damage_amount, 0) > 0
                ORDER BY damage_amount DESC
            """
            params = ()

        elif filter_type == "no_damage":
            query = """
                SELECT 
                    id, full_name, phone, deposit_amount, deposit_status,
                    total_orders, income_from_driver, total_turnover,
                    damage_amount, driver_salary_total, debt
                FROM drivers
                WHERE COALESCE(damage_amount, 0) = 0
                ORDER BY full_name ASC
            """
            params = ()

        elif filter_type == "has_shifts":
            query = """
                SELECT 
                    drivers.id,
                    drivers.full_name,
                    drivers.phone,
                    drivers.deposit_amount,
                    drivers.deposit_status,
                    drivers.total_orders,
                    drivers.income_from_driver,
                    drivers.total_turnover,
                    drivers.damage_amount,
                    drivers.driver_salary_total,
                    drivers.debt
                FROM drivers
                WHERE EXISTS (
                    SELECT 1
                    FROM shifts
                    WHERE shifts.driver_id = drivers.id
                )
                ORDER BY drivers.full_name ASC
            """
            params = ()

        elif filter_type == "no_shifts":
            query = """
                SELECT 
                    drivers.id,
                    drivers.full_name,
                    drivers.phone,
                    drivers.deposit_amount,
                    drivers.deposit_status,
                    drivers.total_orders,
                    drivers.income_from_driver,
                    drivers.total_turnover,
                    drivers.damage_amount,
                    drivers.driver_salary_total,
                    drivers.debt
                FROM drivers
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM shifts
                    WHERE shifts.driver_id = drivers.id
                )
                ORDER BY drivers.full_name ASC
            """
            params = ()

        else:
            return []

        cursor = await db.execute(query, params)
        return await cursor.fetchall()


async def add_deposit_to_driver(driver_id: int, amount: float):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT deposit_amount
            FROM drivers
            WHERE id = ?
        """, (driver_id,))

        driver = await cursor.fetchone()

        if not driver:
            return None

        current_deposit = driver[0] or 0
        new_deposit = current_deposit + amount

        deposit_status = "stopped" if new_deposit >= 20000 else "active"

        await db.execute("""
            UPDATE drivers
            SET 
                deposit_amount = ?,
                deposit_status = ?
            WHERE id = ?
        """, (
            new_deposit,
            deposit_status,
            driver_id
        ))

        await db.commit()

        return new_deposit


async def update_driver_shift_totals(
    driver_id: int,
    orders_count: int,
    turnover: float,
    driver_salary: float
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE drivers
            SET
                total_orders = COALESCE(total_orders, 0) + ?,
                total_turnover = COALESCE(total_turnover, 0) + ?,
                income_from_driver = COALESCE(income_from_driver, 0) + ?,
                driver_salary_total = COALESCE(driver_salary_total, 0) + ?
            WHERE id = ?
        """, (
            orders_count,
            turnover,
            turnover,
            driver_salary,
            driver_id
        ))

        await db.commit()


async def add_driver_debt(driver_id: int, amount: float):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE drivers
            SET 
                debt = COALESCE(debt, 0) + ?,
                damage_amount = COALESCE(damage_amount, 0) + ?
            WHERE id = ?
        """, (
            amount,
            amount,
            driver_id
        ))

        await db.commit()


async def get_driver_shift_history(driver_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                shifts.id,
                cars.plate_number,
                cars.model,
                shifts.orders_count,
                shifts.turnover,
                shifts.driver_salary,
                shifts.fuel_expense,
                shifts.yandex_commission,
                shifts.battery_percent,
                shifts.start_time,
                shifts.end_time
            FROM shifts
            JOIN cars ON shifts.car_id = cars.id
            WHERE shifts.driver_id = ?
            ORDER BY shifts.id DESC
            LIMIT 30
        """, (driver_id,))

        return await cursor.fetchall()


async def get_driver_income_history(driver_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                shifts.id,
                shifts.turnover,
                shifts.driver_salary,
                shifts.salary_percent,
                shifts.recommended_salary,
                shifts.end_time
            FROM shifts
            WHERE shifts.driver_id = ?
            AND shifts.status = 'finished'
            ORDER BY shifts.id DESC
            LIMIT 30
        """, (driver_id,))

        return await cursor.fetchall()


async def get_driver_income_summary(driver_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                COUNT(id),
                COALESCE(SUM(orders_count), 0),
                COALESCE(SUM(turnover), 0),
                COALESCE(SUM(driver_salary), 0),
                COALESCE(AVG(turnover), 0),
                COALESCE(AVG(driver_salary), 0)
            FROM shifts
            WHERE driver_id = ?
            AND status = 'finished'
        """, (driver_id,))

        return await cursor.fetchone()


async def get_drivers_rating():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                drivers.id,
                drivers.full_name,
                COUNT(shifts.id) AS shifts_count,
                COALESCE(SUM(shifts.orders_count), 0) AS total_orders,
                COALESCE(SUM(shifts.turnover), 0) AS total_turnover,
                COALESCE(SUM(shifts.driver_salary), 0) AS total_salary,
                COALESCE(AVG(shifts.turnover), 0) AS avg_turnover,
                COALESCE(drivers.debt, 0) AS debt,
                COALESCE(drivers.damage_amount, 0) AS damage_amount
            FROM drivers
            LEFT JOIN shifts ON drivers.id = shifts.driver_id 
                AND shifts.status = 'finished'
            GROUP BY drivers.id
            ORDER BY 
                total_turnover DESC,
                total_orders DESC,
                debt ASC
        """)

        return await cursor.fetchall()