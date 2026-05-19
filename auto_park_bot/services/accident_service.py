import aiosqlite

from database import DB_NAME
from services.car_service import update_car_status
from services.driver_service import add_driver_debt
from services.shift_service import get_shift_full_by_id


def calculate_difference(estimate_amount: float, repair_fact: float, losses_amount: float) -> float:
    return (estimate_amount or 0) - (repair_fact or 0) - (losses_amount or 0)


async def create_accident(
    shift_id: int,
    accident_date: str,
    accident_place: str,
    accident_type: str,
    guilty_party: str,
    repair_fact: float,
    estimate_amount: float,
    payment_type: str,
    paid_amount: float,
    downtime_shifts: int,
    losses_amount: float,
    photo_1: str,
    photo_2: str,
    note: str
):
    shift = await get_shift_full_by_id(shift_id)

    if not shift:
        return None

    driver_id = shift["driver_id"]
    car_id = shift["car_id"]

    damage_amount = estimate_amount or 0
    debt_amount = damage_amount - (paid_amount or 0)

    if debt_amount < 0:
        debt_amount = 0

    difference_amount = calculate_difference(
        estimate_amount=estimate_amount,
        repair_fact=repair_fact,
        losses_amount=losses_amount
    )

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO accidents (
                shift_id,
                driver_id,
                car_id,
                accident_date,
                accident_place,
                accident_type,
                guilty_party,
                repair_fact,
                estimate_amount,
                damage_amount,
                payment_type,
                paid_amount,
                debt_amount,
                downtime_shifts,
                losses_amount,
                difference_amount,
                photo_1,
                photo_2,
                note,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shift_id,
            driver_id,
            car_id,
            accident_date,
            accident_place,
            accident_type,
            guilty_party,
            repair_fact,
            estimate_amount,
            damage_amount,
            payment_type,
            paid_amount,
            debt_amount,
            downtime_shifts,
            losses_amount,
            difference_amount,
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
                accidents.status,
                accidents.accident_place,
                accidents.accident_type,
                accidents.guilty_party,
                accidents.repair_fact,
                accidents.estimate_amount,
                accidents.downtime_shifts,
                accidents.losses_amount,
                accidents.difference_amount
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
                closed_at,
                accident_place,
                accident_type,
                guilty_party,
                repair_fact,
                estimate_amount,
                downtime_shifts,
                losses_amount,
                difference_amount
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
        "note",
        "accident_place",
        "accident_type",
        "guilty_party",
        "repair_fact",
        "estimate_amount",
        "downtime_shifts",
        "losses_amount",
        "difference_amount",
    }

    if field_name not in allowed_fields:
        return False

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"""
            UPDATE accidents
            SET {field_name} = ?,
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

    paid_amount = accident[7] or 0
    repair_fact = accident[19] or 0
    estimate_amount = accident[20] or 0
    losses_amount = accident[22] or 0

    damage_amount = estimate_amount
    debt_amount = damage_amount - paid_amount

    if debt_amount < 0:
        debt_amount = 0

    difference_amount = calculate_difference(
        estimate_amount=estimate_amount,
        repair_fact=repair_fact,
        losses_amount=losses_amount
    )

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE accidents
            SET damage_amount = ?,
                debt_amount = ?,
                difference_amount = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            damage_amount,
            debt_amount,
            difference_amount,
            accident_id
        ))

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
            SET status = 'closed',
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


async def get_accidents_for_excel():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
            SELECT
                accidents.id,
                accidents.accident_date,
                cars.plate_number,
                drivers.full_name,
                accidents.accident_place,
                accidents.accident_type,
                accidents.guilty_party,
                accidents.repair_fact,
                accidents.estimate_amount,
                accidents.payment_type,
                accidents.status,
                accidents.downtime_shifts,
                accidents.losses_amount,
                accidents.difference_amount,
                accidents.paid_amount,
                accidents.debt_amount,
                accidents.note
            FROM accidents
            LEFT JOIN drivers ON accidents.driver_id = drivers.id
            LEFT JOIN cars ON accidents.car_id = cars.id
            ORDER BY accidents.id ASC
        """)

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]