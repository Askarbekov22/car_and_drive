from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard():
    keyboard = [
        [
            KeyboardButton(text="🚗 Машины"),
            KeyboardButton(text="👤 Водители"),
        ],
        [
            KeyboardButton(text="🔄 Смена"),
            KeyboardButton(text="📊 Отчёты"),
        ],
        [
            KeyboardButton(text="🚨 ДТП"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )