import aiosqlite


class AccidentDB:

    def __init__(self, db_name):
        self.db_name = db_name

    async def create_table(self):
        async with aiosqlite.connect(
                self.db_name
        ) as db:

            await db.execute("""
                CREATE TABLE IF NOT EXISTS accidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shift_id INTEGER,
                    damage_amount INTEGER,
                    payment_type TEXT,
                    paid_amount INTEGER,
                    photo_1 TEXT,
                    photo_2 TEXT,
                    note TEXT,
                    status TEXT DEFAULT 'open'
                )
            """)

            await db.commit()

    async def create_accident(
            self,
            shift_id,
            damage_amount,
            payment_type,
            paid_amount,
            photo_1,
            photo_2,
            note
    ):
        async with aiosqlite.connect(
                self.db_name
        ) as db:

            cursor = await db.execute("""
                INSERT INTO accidents (
                    shift_id,
                    damage_amount,
                    payment_type,
                    paid_amount,
                    photo_1,
                    photo_2,
                    note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                shift_id,
                damage_amount,
                payment_type,
                paid_amount,
                photo_1,
                photo_2,
                note
            ))

            await db.commit()

            return cursor.lastrowid

    async def get_all_accidents(self):
        async with aiosqlite.connect(
                self.db_name
        ) as db:

            cursor = await db.execute("""
                SELECT * FROM accidents
                ORDER BY id DESC
            """)

            rows = await cursor.fetchall()

            accidents = []

            for row in rows:
                accidents.append({
                    "id": row[0],
                    "shift_id": row[1],
                    "damage_amount": row[2],
                    "payment_type": row[3],
                    "paid_amount": row[4],
                    "photo_1": row[5],
                    "photo_2": row[6],
                    "note": row[7],
                    "status": row[8]
                })

            return accidents

    async def close_accident(self, accident_id):
        async with aiosqlite.connect(
                self.db_name
        ) as db:

            await db.execute("""
                UPDATE accidents
                SET status = 'closed'
                WHERE id = ?
            """, (accident_id,))

            await db.commit()