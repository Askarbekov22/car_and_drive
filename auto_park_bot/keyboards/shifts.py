from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def shifts_menu_keyboard():
    keyboard = [
        [KeyboardButton(text="▶️ Начать смену")],
        [KeyboardButton(text="⛔ Завершить смену")],
        [KeyboardButton(text="⬅️ Назад")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def drivers_keyboard(drivers):
    keyboard = []

    for driver in drivers:
        keyboard.append([KeyboardButton(text=driver[1])])

    keyboard.append([KeyboardButton(text="⬅️ Назад")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def cars_keyboard(cars):
    keyboard = []

    for car in cars:
        keyboard.append([KeyboardButton(text=car[1])])

    keyboard.append([KeyboardButton(text="⬅️ Назад")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def active_shifts_keyboard(shifts):
    keyboard = []

    for shift in shifts:
        shift_id = shift[0]
        driver_name = shift[1]
        plate_number = shift[2]

        keyboard.append([
            KeyboardButton(text=f"Смена #{shift_id} | {driver_name} | {plate_number}")
        ])

    keyboard.append([KeyboardButton(text="⬅️ Назад")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )