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
                debt,
                fine_amount_total
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
                deposit_status,
                total_orders,
                income_from_driver,
                total_turnover,
                damage_amount,
                driver_salary_total,
                debt,
                fine_amount_total,
                created_at
            FROM drivers
            WHERE id = ?
        """, (driver_id,))

        return await cursor.fetchone()


async def update_driver_field(driver_id: int, field_name: str, value):
    allowed_fields = {
        "full_name",
        "phone",
        "passport_front",
        "passport_back",
        "address",
        "extra_contact_1",
        "extra_contact_2",
        "hire_date",
        "contract_file",
        "deposit_amount",
        "deposit_receipt",
        "deposit_limit",
        "deposit_status",
        "total_orders",
        "income_from_driver",
        "total_turnover",
        "damage_amount",
        "driver_salary_total",
        "debt",
        "fine_amount_total",
    }

    if field_name not in allowed_fields:
        return False

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            f"""
            UPDATE drivers
            SET {field_name} = ?
            WHERE id = ?
            """,
            (value, driver_id)
        )

        await db.commit()

    return True


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
                debt,
                fine_amount_total
            FROM drivers
            WHERE full_name LIKE ? OR phone LIKE ?
            ORDER BY full_name ASC
        """, (
            search_text,
            search_text
        ))

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
            SET deposit_amount = ?,
                deposit_status = ?
            WHERE id = ?
        """, (
            new_deposit,
            deposit_status,
            driver_id
        ))

        await db.commit()

    return new_deposit


async def deduct_fine_from_driver_deposit(
    driver_id: int,
    shift_id: int,
    amount: float,
    reason: str
):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT deposit_amount, debt
            FROM drivers
            WHERE id = ?
        """, (driver_id,))

        driver = await cursor.fetchone()

        if not driver:
            return None

        current_deposit = driver[0] or 0
        current_debt = driver[1] or 0

        deducted_amount = min(current_deposit, amount)
        remaining_debt = amount - deducted_amount
        new_deposit = current_deposit - deducted_amount
        new_debt = current_debt + remaining_debt
        deposit_status = "stopped" if new_deposit >= 20000 else "active"

        await db.execute("""
            UPDATE drivers
            SET deposit_amount = ?,
                deposit_status = ?,
                debt = ?,
                fine_amount_total = COALESCE(fine_amount_total, 0) + ?
            WHERE id = ?
        """, (
            new_deposit,
            deposit_status,
            new_debt,
            amount,
            driver_id
        ))

        await db.execute("""
            INSERT INTO driver_fines (
                driver_id,
                shift_id,
                amount,
                reason,
                deducted_amount,
                remaining_debt
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            driver_id,
            shift_id,
            amount,
            reason,
            deducted_amount,
            remaining_debt
        ))

        await db.commit()

    return {
        "old_deposit": current_deposit,
        "new_deposit": new_deposit,
        "deducted_amount": deducted_amount,
        "remaining_debt": remaining_debt,
        "new_debt": new_debt
    }


async def get_driver_fines(driver_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                id,
                shift_id,
                amount,
                reason,
                deducted_amount,
                remaining_debt,
                created_at
            FROM driver_fines
            WHERE driver_id = ?
            ORDER BY id DESC
            LIMIT 30
        """, (driver_id,))

        return await cursor.fetchall()


async def update_driver_shift_totals(
    driver_id: int,
    orders_count: int,
    turnover: float,
    driver_salary: float
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE drivers
            SET total_orders = COALESCE(total_orders, 0) + ?,
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
            SET debt = COALESCE(debt, 0) + ?,
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
                shifts.end_time,
                shifts.fine_amount,
                shifts.fine_reason
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
                shifts.end_time,
                shifts.fine_amount,
                shifts.fine_reason
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
                COALESCE(AVG(driver_salary), 0),
                COALESCE(SUM(fine_amount), 0)
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
                COALESCE(drivers.damage_amount, 0) AS damage_amount,
                COALESCE(drivers.fine_amount_total, 0) AS fine_amount_total
            FROM drivers
            LEFT JOIN shifts
                ON drivers.id = shifts.driver_id
               AND shifts.status = 'finished'
            GROUP BY drivers.id
            ORDER BY total_turnover DESC, total_orders DESC, debt ASC
        """)

        return await cursor.fetchall()