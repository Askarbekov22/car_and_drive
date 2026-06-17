from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)


def backup_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📦 Скачать базу"),
                KeyboardButton(text="♻️ Восстановить базу")
            ],
            [
                KeyboardButton(text="⬅️ Главное меню")
            ]
        ],
        resize_keyboard=True
    )