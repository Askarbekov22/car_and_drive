import aiosqlite

from database import DB_NAME


async def add_car(plate_number: str, model: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO cars (plate_number, model, status) VALUES (?, ?, ?)",
            (plate_number, model, "free")
        )
        await db.commit()


async def get_all_cars():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, plate_number, model, status FROM cars ORDER BY id DESC"
        )
        return await cursor.fetchall()


async def update_car_status(car_id: int, status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE cars SET status = ? WHERE id = ?",
            (status, car_id)
        )
        await db.commit()