from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def reports_keyboard():
    keyboard = [
        [KeyboardButton(text="📅 Сегодня")],
        [KeyboardButton(text="📅 Вчера")],
        [KeyboardButton(text="📅 Текущая неделя")],
        [KeyboardButton(text="📅 Текущий месяц")],
        [KeyboardButton(text="📊 Скачать Excel")],
        [KeyboardButton(text="🔄 Актуальные смены")],
        [KeyboardButton(text="🧾 Последние смены")],
        [KeyboardButton(text="⬅️ Назад")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def finished_shifts_keyboard(shifts):
    keyboard = []

    for shift in shifts:
        keyboard.append([
            KeyboardButton(
                text=f"🧾 Смена #{shift[0]} | {shift[1]} | {shift[2]}"
            )
        ])

    keyboard.append([KeyboardButton(text="⬅️ Назад")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )