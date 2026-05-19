from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def accident_menu_keyboard():
    keyboard = [
        [
            KeyboardButton(text="➕ Добавить ДТП"),
            KeyboardButton(text=" Список ДТП"),
        ],
        [
            KeyboardButton(text="✏️ Редактировать ДТП"),
            KeyboardButton(text=" Отчет ДТП"),
        ],
        [
            KeyboardButton(text="📊 Скачать Excel ДТП"),
        ],
        [
            KeyboardButton(text="⬅️ Главное меню"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def payment_type_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="Водитель",
                callback_data="accident_payment_driver"
            )
        ],
        [
            InlineKeyboardButton(
                text="Компания",
                callback_data="accident_payment_company"
            )
        ],
        [
            InlineKeyboardButton(
                text="Страховая / КАСКО",
                callback_data="accident_payment_insurance"
            )
        ],
        [
            InlineKeyboardButton(
                text="Смешанная оплата",
                callback_data="accident_payment_mixed"
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def accident_list_keyboard(accidents):
    keyboard = []

    for accident in accidents:
        accident_id = accident[0]
        status = accident[12]

        keyboard.append([
            InlineKeyboardButton(
                text=f"✏️ Редактировать #{accident_id}",
                callback_data=f"edit_accident_{accident_id}"
            )
        ])

        if status == "open":
            keyboard.append([
                InlineKeyboardButton(
                    text=f"✅ Закрыть ДТП #{accident_id}",
                    callback_data=f"close_accident_{accident_id}"
                )
            ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def edit_accident_fields_keyboard(accident_id):
    keyboard = [
        [
            InlineKeyboardButton(
                text="Дата ДТП",
                callback_data=f"edit_accident_date_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Место ДТП",
                callback_data=f"edit_accident_place_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Тип ДТП",
                callback_data=f"edit_accident_type_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Кто виновен",
                callback_data=f"edit_accident_guilty_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Факт ремонт",
                callback_data=f"edit_accident_repair_fact_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Оценка",
                callback_data=f"edit_accident_estimate_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Кто оплачивает",
                callback_data=f"edit_accident_payment_type_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Оплаченная сумма",
                callback_data=f"edit_accident_paid_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Простой смены",
                callback_data=f"edit_accident_downtime_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Потери",
                callback_data=f"edit_accident_losses_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Заметка",
                callback_data=f"edit_accident_note_{accident_id}"
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def edit_payment_type_keyboard(accident_id):
    keyboard = [
        [
            InlineKeyboardButton(
                text="Водитель",
                callback_data=f"set_payment_driver_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Компания",
                callback_data=f"set_payment_company_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Страховая / КАСКО",
                callback_data=f"set_payment_insurance_{accident_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Смешанная оплата",
                callback_data=f"set_payment_mixed_{accident_id}"
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)