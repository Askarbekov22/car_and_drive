import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db

from handlers import menu, cars, reports, accidents
from handlers.drivers import router as drivers_router
from handlers.shifts import router as shifts_router


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(drivers_router)
dp.include_router(cars.router)
dp.include_router(shifts_router)
dp.include_router(accidents.router)
dp.include_router(reports.router)
dp.include_router(menu.router)


async def main():
    await init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())