from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.main import (
    main_menu_keyboard
)

from services.access_service import (
    get_role_name
)

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id

    role_name = get_role_name(user_id)

    await message.answer(
        f"Добро пожаловать 🚗\n\n"
        f"Ваша роль: {role_name}\n\n"
        f"Выберите раздел:",
        reply_markup=main_menu_keyboard(
            user_id
        )
    )


eply_markup=main_menu_keyboard()
