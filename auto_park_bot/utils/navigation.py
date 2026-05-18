from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.main import main_menu_keyboard


async def go_to_main_menu(
    message: Message,
    state: FSMContext
):
    await state.clear()

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard(
            message.from_user.id
        )
    )