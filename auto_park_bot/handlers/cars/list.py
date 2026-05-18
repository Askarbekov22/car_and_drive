from aiogram import Router
from aiogram.types import Message

from services.car_service import get_all_cars

router = Router()


@router.message(lambda message: message.text == "📋 Список машин")
async def list_cars(message: Message):
    cars = await get_all_cars()

    if not cars:
        await message.answer("Список машин пуст.")
        return

    text = "🚗 Список машин:\n\n"

    for car in cars:
        text += (
            f"ID: {car[0]}\n"
            f"Госномер: {car[1]}\n"
            f"Модель: {car[2]}\n"
            f"Статус: {car[3]}\n\n"
        )

    await message.answer(text)