import aiosqlite

from database import DB_NAME
from services.car_service import update_car_status
from services.driver_service import add_driver_debt
from services.shift_service import get_shift_full_by_id


async def create_accident(
    shift_id: int,
    accident_date: str,
    damage_amount: float,
    payment_type: str,
    paid_amount: float,
    photo_1: str,
    photo_2: str,
    note: str
):
    shift = await get_shift_full_by_id(shift_id)

    if not shift:
        return None

    driver_id = shift["driver_id"]
    car_id = shift["car_id"]

    debt_amount = damage_amount - paid_amount

    if debt_amount < 0:
        debt_amount = 0

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO accidents (
                shift_id,
                driver_id,
                car_id,
                accident_date,
                damage_amount,
                payment_type,
                paid_amount,
                debt_amount,
                photo_1,
                photo_2,
                note,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shift_id,
            driver_id,
            car_id,
            accident_date,
            damage_amount,
            payment_type,
            paid_amount,
            debt_amount,
            photo_1,
            photo_2,
            note,
            "open"
        ))

        await db.commit()
        accident_id = cursor.lastrowid

    await update_car_status(car_id, "repair")

    if payment_type in ["driver", "mixed"] and debt_amount > 0:
        await add_driver_debt(driver_id, debt_amount)

    return accident_id


async def get_all_accidents():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                accidents.id,
                accidents.shift_id,
                drivers.full_name,
                cars.plate_number,
                cars.model,
                accidents.accident_date,
                accidents.damage_amount,
                accidents.payment_type,
                accidents.paid_amount,
                accidents.debt_amount,
                accidents.note,
                accidents.created_at,
                accidents.status
            FROM accidents
            LEFT JOIN drivers ON accidents.driver_id = drivers.id
            LEFT JOIN cars ON accidents.car_id = cars.id
            ORDER BY accidents.id DESC
            LIMIT 50
        """)

        return await cursor.fetchall()


async def get_accident_by_id(accident_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                id,
                shift_id,
                driver_id,
                car_id,
                accident_date,
                damage_amount,
                payment_type,
                paid_amount,
                debt_amount,
                photo_1,
                photo_2,
                note,
                status,
                created_at,
                updated_at,
                closed_at
            FROM accidents
            WHERE id = ?
        """, (accident_id,))

        return await cursor.fetchone()


async def update_accident_field(accident_id: int, field_name: str, value):
    allowed_fields = {
        "accident_date",
        "damage_amount",
        "payment_type",
        "paid_amount",
        "note"
    }

    if field_name not in allowed_fields:
        return False

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"""
            UPDATE accidents
            SET 
                {field_name} = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (value, accident_id))

        await db.commit()

    await recalculate_accident_debt(accident_id)

    return True


async def recalculate_accident_debt(accident_id: int):
    accident = await get_accident_by_id(accident_id)

    if not accident:
        return False

    damage_amount = accident[5] or 0
    paid_amount = accident[7] or 0

    debt_amount = damage_amount - paid_amount

    if debt_amount < 0:
        debt_amount = 0

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE accidents
            SET debt_amount = ?
            WHERE id = ?
        """, (debt_amount, accident_id))

        await db.commit()

    return True


async def close_accident(accident_id: int):
    accident = await get_accident_by_id(accident_id)

    if not accident:
        return False

    car_id = accident[3]

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE accidents
            SET 
                status = 'closed',
                closed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (accident_id,))

        await db.commit()

    if car_id:
        await update_car_status(car_id, "free")

    return True


async def get_accident_report():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                COUNT(id),
                COALESCE(SUM(damage_amount), 0),
                COALESCE(SUM(paid_amount), 0),
                COALESCE(SUM(debt_amount), 0),
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END),
                SUM(CASE WHEN payment_type = 'driver' THEN 1 ELSE 0 END),
                SUM(CASE WHEN payment_type = 'company' THEN 1 ELSE 0 END),
                SUM(CASE WHEN payment_type = 'insurance' THEN 1 ELSE 0 END),
                SUM(CASE WHEN payment_type = 'mixed' THEN 1 ELSE 0 END)
            FROM accidents
        """)

        return await cursor.fetchone()


async def get_accident_report_by_dates(start_date: str, end_date: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                COUNT(id),
                COALESCE(SUM(damage_amount), 0),
                COALESCE(SUM(paid_amount), 0),
                COALESCE(SUM(debt_amount), 0),
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END)
            FROM accidents
            WHERE DATE(accident_date) BETWEEN DATE(?) AND DATE(?)
        """, (start_date, end_date))

        return await cursor.fetchone()