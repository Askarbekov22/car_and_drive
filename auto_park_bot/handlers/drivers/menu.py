from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.drivers import drivers_menu_keyboard

router = Router()


@router.message(lambda message: message.text == "👤 Водители")
async def drivers_menu(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Раздел водителей 👤",
        reply_markup=drivers_menu_keyboard()
    )