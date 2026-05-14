from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def drivers_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="➕ Добавить водителя")],
        [KeyboardButton(text="📋 Список водителей")],
        [KeyboardButton(text="⬅️ Назад")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )