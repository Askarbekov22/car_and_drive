from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def drivers_menu_keyboard():
    keyboard = [
        [
            KeyboardButton(text="➕ Добавить водителя"),
            KeyboardButton(text="📋 Список водителей"),
        ],
        [
            KeyboardButton(text="🔎 Поиск водителя"),
            KeyboardButton(text="🧩 Фильтр водителей"),
        ],
        [
            KeyboardButton(text="🕘 История смен водителя"),
            KeyboardButton(text="💰 История дохода водителя"),
        ],
        [
            KeyboardButton(text="🏆 Рейтинг водителей"),
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def drivers_select_keyboard(drivers):
    keyboard = []

    for driver in drivers:
        full_name = driver[1]

        keyboard.append([
            KeyboardButton(text=full_name)
        ])

    keyboard.append([
        KeyboardButton(text="⬅️ Назад")
    ])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def driver_filter_keyboard():
    keyboard = [
        [
            KeyboardButton(text="✅ Депозит активен"),
            KeyboardButton(text="⛔ Депозит остановлен"),
        ],
        [
            KeyboardButton(text="💸 Есть долг"),
            KeyboardButton(text="✅ Без долга"),
        ],
        [
            KeyboardButton(text="🛠 Есть ущерб"),
            KeyboardButton(text="✅ Без ущерба"),
        ],
        [
            KeyboardButton(text="🚕 Есть смены"),
            KeyboardButton(text="🆕 Без смен"),
        ],
        [
            KeyboardButton(text="⬅️ Назад"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )