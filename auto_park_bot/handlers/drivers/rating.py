from aiogram import Router
from aiogram.types import Message

from services.driver_service import get_drivers_rating

router = Router()


@router.message(lambda message: message.text == "🏆 Рейтинг водителей")
async def show_drivers_rating(message: Message):
    rating = await get_drivers_rating()

    if not rating:
        await message.answer("Рейтинг пуст.")
        return

    text = "🏆 Рейтинг водителей\n\n"

    place = 1

    for row in rating:
        score = (
            (row[3] or 0) * 2
            + (row[4] or 0) / 1000
            - (row[7] or 0) / 1000
            - (row[8] or 0) / 1000
            - (row[9] or 0) / 1000
        )

        text += (
            f"{place}. {row[1]}\n"
            f"Смен: {row[2] or 0}\n"
            f"Заказы: {row[3] or 0}\n"
            f"Оборот: {row[4] or 0:.0f} сом\n"
            f"Средний оборот: {row[6] or 0:.0f} сом\n"
            f"Долг: {row[7] or 0:.0f} сом\n"
            f"Ущерб: {row[8] or 0:.0f} сом\n"
            f"Штрафы: {row[9] or 0:.0f} сом\n"
            f"Рейтинг: {score:.1f}\n\n"
        )

        place += 1

    await message.answer(text)