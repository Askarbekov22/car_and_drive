from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def cars_menu_keyboard():
    keyboard = [
        [
            KeyboardButton(text="➕ Добавить машину"),
            KeyboardButton(text="📋 Список машин"),
        ],
        [
            KeyboardButton(text="✏️ Редактировать машину"),
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def edit_car_fields_keyboard(car_id: int):
    keyboard = [
        [
            InlineKeyboardButton(
                text="Госномер",
                callback_data=f"edit_car_plate_{car_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Модель",
                callback_data=f"edit_car_model_{car_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Статус",
                callback_data=f"edit_car_status_{car_id}"
            )
        ],
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )