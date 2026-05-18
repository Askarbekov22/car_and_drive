from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

from services.access_service import (
    can_open_section
)


def main_menu_keyboard(user_id=None):

    keyboard = []

    first_row = []

    if user_id is None or can_open_section(
        user_id,
        "cars"
    ):
        first_row.append(
            KeyboardButton(text="🚗 Машины")
        )

    if user_id is None or can_open_section(
        user_id,
        "drivers"
    ):
        first_row.append(
            KeyboardButton(text="👤 Водители")
        )

    if first_row:
        keyboard.append(first_row)

    second_row = []

    if user_id is None or can_open_section(
        user_id,
        "shifts"
    ):
        second_row.append(
            KeyboardButton(text="🔄 Смена")
        )

    if user_id is None or can_open_section(
        user_id,
        "accidents"
    ):
        second_row.append(
            KeyboardButton(text="🚨 ДТП")
        )

    if second_row:
        keyboard.append(second_row)

    third_row = []

    if user_id is None or can_open_section(
        user_id,
        "reports"
    ):
        third_row.append(
            KeyboardButton(text="📊 Отчёты")
        )

    if third_row:
        keyboard.append(third_row)

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )