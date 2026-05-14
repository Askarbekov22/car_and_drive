from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def cars_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="➕ Добавить машину")],
        [KeyboardButton(text="📋 Список машин")],
        [KeyboardButton(text="⬅️ Назад")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )