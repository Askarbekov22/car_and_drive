from aiogram import Router
from aiogram.types import Message

from keyboards.accident_keyboards import accident_list_keyboard

from services.accident_service import get_all_accidents

router = Router()


@router.message(lambda message: message.text == "📋 Список ДТП")
async def list_accidents(message: Message):
    accidents = await get_all_accidents()

    if not accidents:
        await message.answer("ДТП пока нет.")
        return

    payment_names = {
        "driver": "Водитель",
        "company": "Компания",
        "insurance": "Страховая",
        "mixed": "Смешанная оплата"
    }

    text = "📋 Список ДТП:\n\n"

    for accident in accidents:
        text += (
            f"🚨 ДТП #{accident[0]}\n"
            f"Смена: {accident[1]}\n"
            f"Водитель: {accident[2]}\n"
            f"Машина: {accident[3]} {accident[4]}\n"
            f"Дата ДТП: {accident[5]}\n"
            f"Ущерб: {accident[6]} сом\n"
            f"Оплачивает: {payment_names.get(accident[7], accident[7])}\n"
            f"Оплачено: {accident[8]} сом\n"
            f"Остаток: {accident[9]} сом\n"
            f"Заметка: {accident[10]}\n"
            f"Создано: {accident[11]}\n"
            f"Статус: {accident[12]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=accident_list_keyboard(accidents)
    )