from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard(user_id=None):

    keyboard = [
        [
            KeyboardButton(text="🚗 Машины"),
            KeyboardButton(text="👤 Водители")
        ],
        [
            KeyboardButton(text="🔄 Смена"),
            KeyboardButton(text="🚨 ДТП")
        ],
        [
            KeyboardButton(text="📊 Отчёты")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )