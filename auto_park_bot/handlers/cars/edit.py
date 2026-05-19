from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.access_service import can_edit_data

router = Router()


@router.message(lambda message: message.text == "✏️ Редактировать машину")
async def start_edit_car(message: Message, state: FSMContext):

    if not can_edit_data(message.from_user.id):
        await message.answer(
            "⛔ Редактировать машины могут только Ырыс и Сыймык."
        )
        return

    await state.clear()

    await message.answer(
        "Введите ID машины для редактирования:"
    )