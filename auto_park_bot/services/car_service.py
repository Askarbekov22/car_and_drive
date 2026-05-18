import aiosqlite

from database import DB_NAME

from constants.car_statuses import (
    STATUS_FREE,
    STATUS_BUSY,
    STATUS_REPAIR
)


async def add_car(
    plate_number: str,
    model: str
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT INTO cars (
                plate_number,
                model,
                status
            )
            VALUES (?, ?, ?)
            """,
            (
                plate_number,
                model,
                STATUS_FREE
            )
        )

        await db.commit()


async def get_all_cars():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                id,
                plate_number,
                model,
                status
            FROM cars
            ORDER BY id DESC
            """
        )

        return await cursor.fetchall()


async def get_car_by_id(car_id: int):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                id,
                plate_number,
                model,
                status
            FROM cars
            WHERE id = ?
            """,
            (car_id,)
        )

        return await cursor.fetchone()


async def update_car_status(
    car_id: int,
    status: str
):

    allowed_statuses = [
        STATUS_FREE,
        STATUS_BUSY,
        STATUS_REPAIR
    ]

    if status not in allowed_statuses:
        return False

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE cars
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                car_id
            )
        )

        await db.commit()

    return True


async def update_car_field(
    car_id: int,
    field_name: str,
    value: str
):

    allowed_fields = {
        "plate_number",
        "model",
        "status"
    }

    if field_name not in allowed_fields:
        return False

    if field_name == "status":

        allowed_statuses = [
            STATUS_FREE,
            STATUS_BUSY,
            STATUS_REPAIR
        ]

        if value not in allowed_statuses:
            return False

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            f"""
            UPDATE cars
            SET {field_name} = ?
            WHERE id = ?
            """,
            (
                value,
                car_id
            )
        )

        await db.commit()

    return True