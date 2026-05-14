from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.main import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать в бот автопарка 🚗\n\n"
        "Выберите раздел:",
        reply_markup=main_menu_keyboard()
    )