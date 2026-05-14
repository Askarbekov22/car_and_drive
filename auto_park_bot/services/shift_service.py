import aiosqlite

from database import DB_NAME


def calculate_driver_salary(turnover: float):
    if turnover <= 3000:
        percent = 25

    elif turnover <= 4000:
        percent = 30

    elif turnover <= 8000:
        percent = 35

    else:
        percent = 40

    salary = turnover * percent / 100

    return salary, percent


async def create_shift(
    driver_id,
    car_id,
    start_front_photo,
    start_back_photo,
    start_left_photo,
    start_right_photo
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO shifts (
                driver_id,
                car_id,
                start_front_photo,
                start_back_photo,
                start_left_photo,
                start_right_photo
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            driver_id,
            car_id,
            start_front_photo,
            start_back_photo,
            start_left_photo,
            start_right_photo
        ))

        await db.execute(
            "UPDATE cars SET status = 'busy' WHERE id = ?",
            (car_id,)
        )

        await db.commit()


async def get_active_shifts():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT 
                shifts.id,
                drivers.full_name,
                cars.plate_number,
                cars.model
            FROM shifts
            JOIN drivers ON shifts.driver_id = drivers.id
            JOIN cars ON shifts.car_id = cars.id
            WHERE shifts.status = 'active'
            ORDER BY shifts.id DESC
        """)

        return await cursor.fetchall()


async def get_shift_driver_id(shift_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT driver_id
            FROM shifts
            WHERE id = ?
        """, (shift_id,))

        result = await cursor.fetchone()

        if not result:
            return None

        return result[0]


async def finish_shift(
    shift_id: int,
    orders_count: int,
    turnover: float,
    cash: float,
    card: float,
    charging_expense: float,
    yandex_commission: float,
    driver_salary: float,
    battery_percent: int,
    front_photo: str,
    back_photo: str,
    left_photo: str,
    right_photo: str,
    charging_receipt: str
):
    recommended_salary, salary_percent = calculate_driver_salary(turnover)

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
            UPDATE shifts
            SET 
                status = 'finished',
                end_time = CURRENT_TIMESTAMP,

                orders_count = ?,
                turnover = ?,

                cash = ?,
                card = ?,

                fuel_expense = ?,
                yandex_commission = ?,

                driver_salary = ?,
                battery_percent = ?,

                front_photo = ?,
                back_photo = ?,
                left_photo = ?,
                right_photo = ?,

                charging_receipt = ?,

                salary_percent = ?,
                recommended_salary = ?

            WHERE id = ?
        """, (
            orders_count,
            turnover,

            cash,
            card,

            charging_expense,
            yandex_commission,

            driver_salary,
            battery_percent,

            front_photo,
            back_photo,
            left_photo,
            right_photo,

            charging_receipt,

            salary_percent,
            recommended_salary,

            shift_id
        ))

        cursor = await db.execute("""
            SELECT car_id
            FROM shifts
            WHERE id = ?
        """, (shift_id,))

        car = await cursor.fetchone()

        if car:
            await db.execute("""
                UPDATE cars
                SET status = 'free'
                WHERE id = ?
            """, (car[0],))

        await db.commit()


async def get_finished_shifts():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT 
                shifts.id,

                drivers.full_name,

                cars.plate_number,
                cars.model,

                shifts.orders_count,
                shifts.turnover,

                shifts.cash,
                shifts.card,

                shifts.fuel_expense,
                shifts.yandex_commission,

                shifts.driver_salary,
                shifts.salary_percent,
                shifts.recommended_salary,

                shifts.battery_percent,

                shifts.start_time,
                shifts.end_time

            FROM shifts

            JOIN drivers 
            ON shifts.driver_id = drivers.id

            JOIN cars 
            ON shifts.car_id = cars.id

            WHERE shifts.status = 'finished'

            ORDER BY shifts.id DESC

            LIMIT 20
        """)

        return await cursor.fetchall()


async def get_shift_by_id(shift_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT 
                shifts.id,

                drivers.full_name,

                cars.plate_number,
                cars.model,

                shifts.orders_count,
                shifts.turnover,

                shifts.cash,
                shifts.card,

                shifts.fuel_expense,
                shifts.yandex_commission,

                shifts.driver_salary,
                shifts.salary_percent,
                shifts.recommended_salary,

                shifts.battery_percent,

                shifts.start_time,
                shifts.end_time,

                shifts.start_front_photo,
                shifts.start_back_photo,
                shifts.start_left_photo,
                shifts.start_right_photo,

                shifts.front_photo,
                shifts.back_photo,
                shifts.left_photo,
                shifts.right_photo,

                shifts.charging_receipt

            FROM shifts

            JOIN drivers 
            ON shifts.driver_id = drivers.id

            JOIN cars 
            ON shifts.car_id = cars.id

            WHERE shifts.id = ?
        """, (shift_id,))

        return await cursor.fetchone()


async def get_shift_full_by_id(shift_id: int):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
            SELECT
                shifts.id,
                shifts.driver_id,
                shifts.car_id,

                drivers.full_name,

                cars.plate_number,
                cars.model,

                shifts.status

            FROM shifts

            JOIN drivers 
            ON shifts.driver_id = drivers.id

            JOIN cars 
            ON shifts.car_id = cars.id

            WHERE shifts.id = ?
        """, (shift_id,))

        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "driver_id": row[1],
            "car_id": row[2],
            "driver_name": row[3],
            "plate_number": row[4],
            "car_model": row[5],
            "status": row[6],
        }


async def get_shifts_by_period(
    start_date: str,
    end_date: str
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
            SELECT 
                shifts.id,

                drivers.full_name,

                cars.plate_number,

                shifts.orders_count,
                shifts.turnover,

                shifts.fuel_expense,
                shifts.yandex_commission,

                shifts.driver_salary,
                shifts.salary_percent,
                shifts.recommended_salary,

                shifts.end_time

            FROM shifts

            JOIN drivers 
            ON shifts.driver_id = drivers.id

            JOIN cars 
            ON shifts.car_id = cars.id

            WHERE shifts.status = 'finished'

            AND DATE(shifts.end_time)
            BETWEEN DATE(?) AND DATE(?)

            ORDER BY shifts.end_time DESC
        """, (
            start_date,
            end_date
        ))

        return await cursor.fetchall()