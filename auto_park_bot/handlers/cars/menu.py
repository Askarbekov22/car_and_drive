from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.cars import cars_menu_keyboard
from keyboards.main import main_menu_keyboard

router = Router()


@router.message(lambda message: message.text == "🚗 Машины")
async def cars_menu(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Раздел машин 🚗",
        reply_markup=cars_menu_keyboard()
    )


@router.message(lambda message: message.text == "⬅️ Назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard(message.from_user.id)
    )