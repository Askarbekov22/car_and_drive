from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.shifts import (
    shifts_menu_keyboard,
    drivers_keyboard,
    cars_keyboard,
    active_shifts_keyboard
)

from keyboards.main import main_menu_keyboard

from services.driver_service import (
    get_all_drivers,
    add_deposit_to_driver,
    update_driver_shift_totals
)

from services.car_service import get_all_cars

from services.shift_service import (
    create_shift,
    get_active_shifts,
    finish_shift,
    get_shift_driver_id,
    calculate_driver_salary
)

router = Router()


class ShiftState(StatesGroup):
    choosing_driver = State()
    choosing_car = State()

    start_front_photo = State()
    start_back_photo = State()
    start_left_photo = State()
    start_right_photo = State()

    choosing_shift_to_finish = State()

    front_photo = State()
    back_photo = State()
    left_photo = State()
    right_photo = State()

    battery_percent = State()

    orders_count = State()
    turnover = State()
    cash = State()
    card = State()

    charging_expense = State()
    charging_receipt = State()

    yandex_commission = State()

    driver_salary = State()

    deposit_top_up = State()
    deposit_receipt = State()


@router.message(lambda message: message.text == "🔄 Смена")
async def shifts_menu(message: Message):
    await message.answer(
        "Раздел смен 🔄",
        reply_markup=shifts_menu_keyboard()
    )


@router.message(lambda message: message.text == "▶️ Начать смену")
async def start_shift(message: Message, state: FSMContext):
    drivers = await get_all_drivers()

    if not drivers:
        await message.answer("Нет водителей.")
        return

    await message.answer(
        "Выберите водителя:",
        reply_markup=drivers_keyboard(drivers)
    )

    await state.set_state(ShiftState.choosing_driver)


@router.message(ShiftState.choosing_driver)
async def choose_driver(message: Message, state: FSMContext):

    if message.text == "⬅️ Назад":
        await state.clear()

        await message.answer(
            "Раздел смен 🔄",
            reply_markup=shifts_menu_keyboard()
        )

        return

    drivers = await get_all_drivers()

    driver_dict = {
        driver[1]: driver[0]
        for driver in drivers
    }

    if message.text not in driver_dict:
        await message.answer("Выбери водителя из списка.")
        return

    await state.update_data(
        driver_id=driver_dict[message.text]
    )

    cars = await get_all_cars()

    free_cars = [
        car for car in cars
        if car[3] == "free"
    ]

    if not free_cars:
        await message.answer("Нет свободных машин.")
        await state.clear()
        return

    await message.answer(
        "Выберите машину:",
        reply_markup=cars_keyboard(free_cars)
    )

    await state.set_state(ShiftState.choosing_car)


@router.message(ShiftState.choosing_car)
async def choose_car(message: Message, state: FSMContext):

    if message.text == "⬅️ Назад":
        await state.clear()

        await message.answer(
            "Раздел смен 🔄",
            reply_markup=shifts_menu_keyboard()
        )

        return

    cars = await get_all_cars()

    free_cars = [
        car for car in cars
        if car[3] == "free"
    ]

    car_dict = {
        car[1]: car[0]
        for car in free_cars
    }

    if message.text not in car_dict:
        await message.answer("Выбери машину из списка.")
        return

    await state.update_data(
        car_id=car_dict[message.text]
    )

    await message.answer(
        "📸 Начало смены: отправь фото ПЕРЕДА машины:"
    )

    await state.set_state(
        ShiftState.start_front_photo
    )


@router.message(ShiftState.start_front_photo)
async def get_start_front_photo(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(
        start_front_photo=message.photo[-1].file_id
    )

    await message.answer(
        "📸 Начало смены: отправь фото ЗАДА машины:"
    )

    await state.set_state(
        ShiftState.start_back_photo
    )


@router.message(ShiftState.start_back_photo)
async def get_start_back_photo(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(
        start_back_photo=message.photo[-1].file_id
    )

    await message.answer(
        "📸 Начало смены: отправь фото ЛЕВОЙ стороны:"
    )

    await state.set_state(
        ShiftState.start_left_photo
    )


@router.message(ShiftState.start_left_photo)
async def get_start_left_photo(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(
        start_left_photo=message.photo[-1].file_id
    )

    await message.answer(
        "📸 Начало смены: отправь фото ПРАВОЙ стороны:"
    )

    await state.set_state(
        ShiftState.start_right_photo
    )


@router.message(ShiftState.start_right_photo)
async def get_start_right_photo(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(
        start_right_photo=message.photo[-1].file_id
    )

    data = await state.get_data()

    await create_shift(
        driver_id=data["driver_id"],
        car_id=data["car_id"],
        start_front_photo=data["start_front_photo"],
        start_back_photo=data["start_back_photo"],
        start_left_photo=data["start_left_photo"],
        start_right_photo=data["start_right_photo"]
    )

    await message.answer(
        "✅ Смена начата",
        reply_markup=shifts_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "⛔ Завершить смену")
async def start_finish_shift(message: Message, state: FSMContext):

    shifts = await get_active_shifts()

    if not shifts:
        await message.answer("Активных смен нет.")
        return

    await message.answer(
        "Выберите смену:",
        reply_markup=active_shifts_keyboard(shifts)
    )

    await state.set_state(
        ShiftState.choosing_shift_to_finish
    )


@router.message(ShiftState.choosing_shift_to_finish)
async def choose_shift(message: Message, state: FSMContext):

    if message.text == "⬅️ Назад":
        await state.clear()

        await message.answer(
            "Раздел смен 🔄",
            reply_markup=shifts_menu_keyboard()
        )

        return

    if not message.text.startswith("Смена #"):
        await message.answer("Выбери смену из списка.")
        return

    shift_id = int(
        message.text.split("|")[0]
        .replace("Смена #", "")
        .strip()
    )

    await state.update_data(
        shift_id=shift_id
    )

    await message.answer(
        "📸 Завершение смены: отправь фото ПЕРЕДА машины:"
    )

    await state.set_state(
        ShiftState.front_photo
    )


@router.message(ShiftState.front_photo)
async def get_front_photo(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(
        front_photo=message.photo[-1].file_id
    )

    await message.answer(
        "📸 Завершение смены: отправь фото ЗАДА машины:"
    )

    await state.set_state(
        ShiftState.back_photo
    )


@router.message(ShiftState.back_photo)
async def get_back_photo(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(
        back_photo=message.photo[-1].file_id
    )

    await message.answer(
        "📸 Завершение смены: отправь фото ЛЕВОЙ стороны:"
    )

    await state.set_state(
        ShiftState.left_photo
    )


@router.message(ShiftState.left_photo)
async def get_left_photo(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(
        left_photo=message.photo[-1].file_id
    )

    await message.answer(
        "📸 Завершение смены: отправь фото ПРАВОЙ стороны:"
    )

    await state.set_state(
        ShiftState.right_photo
    )


@router.message(ShiftState.right_photo)
async def get_right_photo(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(
        right_photo=message.photo[-1].file_id
    )

    await message.answer(
        "🔋 Введите заряд машины (%):"
    )

    await state.set_state(
        ShiftState.battery_percent
    )


@router.message(ShiftState.battery_percent)
async def get_battery_percent(message: Message, state: FSMContext):

    try:
        battery_percent = int(message.text)

        if battery_percent < 0 or battery_percent > 100:
            await message.answer(
                "Заряд должен быть от 0 до 100."
            )
            return

    except ValueError:
        await message.answer(
            "Введите число. Например: 75"
        )
        return

    await state.update_data(
        battery_percent=battery_percent
    )

    await message.answer(
        "Введите количество заказов:"
    )

    await state.set_state(
        ShiftState.orders_count
    )


@router.message(ShiftState.orders_count)
async def get_orders_count(message: Message, state: FSMContext):

    try:
        orders_count = int(message.text)

    except ValueError:
        await message.answer(
            "Введите число. Например: 35"
        )
        return

    await state.update_data(
        orders_count=orders_count
    )

    await message.answer(
        "Введите оборот:"
    )

    await state.set_state(
        ShiftState.turnover
    )


@router.message(ShiftState.turnover)
async def get_turnover(message: Message, state: FSMContext):

    try:
        turnover = float(
            message.text.replace(",", ".")
        )

    except ValueError:
        await message.answer(
            "Введите сумму числом. Например: 12500"
        )
        return

    await state.update_data(
        turnover=turnover
    )

    await message.answer(
        "Введите наличку:"
    )

    await state.set_state(
        ShiftState.cash
    )


@router.message(ShiftState.cash)
async def get_cash(message: Message, state: FSMContext):

    try:
        cash = float(
            message.text.replace(",", ".")
        )

    except ValueError:
        await message.answer(
            "Введите сумму числом."
        )
        return

    await state.update_data(
        cash=cash
    )

    await message.answer(
        "Введите карту / безнал:"
    )

    await state.set_state(
        ShiftState.card
    )


@router.message(ShiftState.card)
async def get_card(message: Message, state: FSMContext):

    try:
        card = float(
            message.text.replace(",", ".")
        )

    except ValueError:
        await message.answer(
            "Введите сумму числом."
        )
        return

    await state.update_data(
        card=card
    )

    await message.answer(
        "Введите расход на зарядку:"
    )

    await state.set_state(
        ShiftState.charging_expense
    )


@router.message(ShiftState.charging_expense)
async def get_charging_expense(message: Message, state: FSMContext):

    try:
        charging_expense = float(
            message.text.replace(",", ".")
        )

    except ValueError:
        await message.answer(
            "Введите сумму числом."
        )
        return

    await state.update_data(
        charging_expense=charging_expense
    )

    await message.answer(
        "🧾 Прикрепите чек за зарядку:"
    )

    await state.set_state(
        ShiftState.charging_receipt
    )


@router.message(ShiftState.charging_receipt)
async def get_charging_receipt(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer(
            "Нужно отправить фото чека."
        )
        return

    await state.update_data(
        charging_receipt=message.photo[-1].file_id
    )

    await message.answer(
        "Введите комиссию Яндекса:"
    )

    await state.set_state(
        ShiftState.yandex_commission
    )


@router.message(ShiftState.yandex_commission)
async def get_yandex_commission(message: Message, state: FSMContext):

    try:
        yandex_commission = float(
            message.text.replace(",", ".")
        )

    except ValueError:
        await message.answer(
            "Введите сумму числом."
        )
        return

    data = await state.get_data()

    turnover = data["turnover"]

    recommended_salary, salary_percent = (
        calculate_driver_salary(turnover)
    )

    await state.update_data(
        yandex_commission=yandex_commission,
        recommended_salary=recommended_salary,
        salary_percent=salary_percent
    )

    await message.answer(
        f"🤖 Рекомендуемая зарплата водителя:\n\n"
        f"Оборот: {turnover:.0f} сом\n"
        f"Процент: {salary_percent}%\n"
        f"Рекомендуемая сумма: "
        f"{recommended_salary:.0f} сом\n\n"
        f"Введите итоговую зарплату водителя:"
    )

    await state.set_state(
        ShiftState.driver_salary
    )


@router.message(ShiftState.driver_salary)
async def get_driver_salary(message: Message, state: FSMContext):

    try:
        driver_salary = float(
            message.text.replace(",", ".")
        )

    except ValueError:
        await message.answer(
            "Введите сумму числом."
        )
        return

    await state.update_data(
        driver_salary=driver_salary
    )

    await message.answer(
        "Введите сумму пополнения депозита.\n"
        "Если пополнения нет — введите 0:"
    )

    await state.set_state(
        ShiftState.deposit_top_up
    )


@router.message(ShiftState.deposit_top_up)
async def get_deposit_top_up(message: Message, state: FSMContext):

    try:
        deposit_top_up = float(
            message.text.replace(",", ".")
        )

        if deposit_top_up < 0:
            await message.answer(
                "Сумма не может быть меньше 0."
            )
            return

    except ValueError:
        await message.answer(
            "Введите сумму числом."
        )
        return

    await state.update_data(
        deposit_top_up=deposit_top_up
    )

    if deposit_top_up > 0:

        await message.answer(
            "🧾 Отправьте фото чека депозита:"
        )

        await state.set_state(
            ShiftState.deposit_receipt
        )

    else:

        await finish_shift_final(
            message,
            state,
            deposit_receipt=None
        )


@router.message(ShiftState.deposit_receipt)
async def get_deposit_receipt(message: Message, state: FSMContext):

    if not message.photo:
        await message.answer(
            "Нужно отправить фото чека."
        )
        return

    await finish_shift_final(
        message,
        state,
        deposit_receipt=message.photo[-1].file_id
    )


async def finish_shift_final(
    message: Message,
    state: FSMContext,
    deposit_receipt: str | None
):
    data = await state.get_data()

    shift_id = data["shift_id"]

    orders_count = data["orders_count"]
    turnover = data["turnover"]

    cash = data["cash"]
    card = data["card"]

    charging_expense = data["charging_expense"]

    yandex_commission = data["yandex_commission"]

    driver_salary = data["driver_salary"]

    recommended_salary = data["recommended_salary"]
    salary_percent = data["salary_percent"]

    deposit_top_up = data["deposit_top_up"]

    driver_id = await get_shift_driver_id(
        shift_id
    )

    await finish_shift(
        shift_id=shift_id,
        orders_count=orders_count,
        turnover=turnover,
        cash=cash,
        card=card,
        charging_expense=charging_expense,
        yandex_commission=yandex_commission,
        driver_salary=driver_salary,
        battery_percent=data["battery_percent"],
        front_photo=data["front_photo"],
        back_photo=data["back_photo"],
        left_photo=data["left_photo"],
        right_photo=data["right_photo"],
        charging_receipt=data["charging_receipt"]
    )

    if driver_id:

        await update_driver_shift_totals(
            driver_id=driver_id,
            orders_count=orders_count,
            turnover=turnover,
            driver_salary=driver_salary
        )

    new_deposit = None

    if driver_id and deposit_top_up > 0:

        new_deposit = await add_deposit_to_driver(
            driver_id=driver_id,
            amount=deposit_top_up
        )

    total_expenses = (
        charging_expense
        + yandex_commission
        + driver_salary
    )

    profit = turnover - total_expenses

    text = (
        "✅ Смена закрыта\n\n"

        f"Заказы: {orders_count}\n"
        f"Оборот: {turnover:.0f} сом\n"

        f"Наличка: {cash:.0f} сом\n"
        f"Карта / безнал: {card:.0f} сом\n\n"

        f"Заряд машины: "
        f"{data['battery_percent']}%\n"

        f"Расход на зарядку: "
        f"{charging_expense:.0f} сом\n"

        f"Комиссия Яндекса: "
        f"{yandex_commission:.0f} сом\n\n"

        f"🤖 Рекомендуемая зарплата:\n"
        f"{recommended_salary:.0f} сом "
        f"({salary_percent}%)\n"

        f"💵 Фактическая зарплата:\n"
        f"{driver_salary:.0f} сом\n\n"

        f"Итого расходы: "
        f"{total_expenses:.0f} сом\n"

        f"Прибыль: "
        f"{profit:.0f} сом\n\n"
    )

    if deposit_top_up > 0 and new_deposit is not None:

        text += (
            f"💰 Пополнение депозита: "
            f"{deposit_top_up:.0f} сом\n"

            f"Текущий депозит: "
            f"{new_deposit:.0f} сом\n"
        )

        if new_deposit >= 20000:

            text += (
                "\n⚠️ Депозит достиг "
                "20 000 сом.\n"

                "Накопление нужно остановить."
            )

        else:

            text += (
                f"До лимита осталось: "
                f"{20000 - new_deposit:.0f} сом"
            )

    else:
        text += "💰 Пополнения депозита не было."

    await message.answer(
        text,
        reply_markup=shifts_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "⬅️ Назад")
async def back(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "Главное меню",
        reply_markup=main_menu_keyboard()
    )