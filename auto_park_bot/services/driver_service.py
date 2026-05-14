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
            ORDER BY id DESC
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
            ORDER BY id DESC
        """)
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
        """, (new_deposit, deposit_status, driver_id))

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