import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db
from handlers import menu, drivers, cars, shifts, reports, accidents


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(drivers.router)
dp.include_router(cars.router)
dp.include_router(shifts.router)
dp.include_router(reports.router)
dp.include_router(accidents.router)
dp.include_router(menu.router)


async def main():
    await init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())