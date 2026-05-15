from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.shifts import (
    active_shifts_keyboard,
    shifts_menu_keyboard
)

from services.shift_service import (
    get_active_shifts,
    finish_shift,
    get_shift_driver_id,
    calculate_driver_salary
)

from services.driver_service import (
    add_deposit_to_driver,
    update_driver_shift_totals,
    deduct_fine_from_driver_deposit
)

router = Router()


class FinishShiftState(StatesGroup):
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

    fine_amount = State()
    fine_reason = State()

    deposit_top_up = State()
    deposit_receipt = State()


@router.message(lambda message: message.text == "⛔ Завершить смену")
async def start_finish_shift(message: Message, state: FSMContext):
    await state.clear()

    shifts = await get_active_shifts()

    if not shifts:
        await message.answer("Активных смен нет.")
        return

    await message.answer(
        "Выберите смену:",
        reply_markup=active_shifts_keyboard(shifts)
    )

    await state.set_state(FinishShiftState.choosing_shift_to_finish)


@router.message(FinishShiftState.choosing_shift_to_finish)
async def choose_shift(message: Message, state: FSMContext):
    if not message.text.startswith("Смена #"):
        await message.answer("Выберите смену из списка.")
        return

    shift_id = int(
        message.text.split("|")[0]
        .replace("Смена #", "")
        .strip()
    )

    await state.update_data(shift_id=shift_id)

    await message.answer("📸 Завершение смены: отправьте фото ПЕРЕДА машины:")
    await state.set_state(FinishShiftState.front_photo)


@router.message(FinishShiftState.front_photo)
async def get_front_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(front_photo=message.photo[-1].file_id)
    await message.answer("📸 Отправьте фото ЗАДА машины:")
    await state.set_state(FinishShiftState.back_photo)


@router.message(FinishShiftState.back_photo)
async def get_back_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(back_photo=message.photo[-1].file_id)
    await message.answer("📸 Отправьте фото ЛЕВОЙ стороны:")
    await state.set_state(FinishShiftState.left_photo)


@router.message(FinishShiftState.left_photo)
async def get_left_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(left_photo=message.photo[-1].file_id)
    await message.answer("📸 Отправьте фото ПРАВОЙ стороны:")
    await state.set_state(FinishShiftState.right_photo)


@router.message(FinishShiftState.right_photo)
async def get_right_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(right_photo=message.photo[-1].file_id)
    await message.answer("🔋 Введите заряд машины (%):")
    await state.set_state(FinishShiftState.battery_percent)


@router.message(FinishShiftState.battery_percent)
async def get_battery_percent(message: Message, state: FSMContext):
    try:
        battery_percent = int(message.text)

        if battery_percent < 0 or battery_percent > 100:
            await message.answer("Заряд должен быть от 0 до 100.")
            return

    except ValueError:
        await message.answer("Введите число. Например: 75")
        return

    await state.update_data(battery_percent=battery_percent)
    await message.answer("Введите количество заказов:")
    await state.set_state(FinishShiftState.orders_count)


@router.message(FinishShiftState.orders_count)
async def get_orders_count(message: Message, state: FSMContext):
    try:
        orders_count = int(message.text)

    except ValueError:
        await message.answer("Введите число. Например: 35")
        return

    await state.update_data(orders_count=orders_count)
    await message.answer("Введите оборот:")
    await state.set_state(FinishShiftState.turnover)


@router.message(FinishShiftState.turnover)
async def get_turnover(message: Message, state: FSMContext):
    try:
        turnover = float(message.text.replace(",", "."))

    except ValueError:
        await message.answer("Введите сумму числом. Например: 12500")
        return

    await state.update_data(turnover=turnover)
    await message.answer("Введите наличку:")
    await state.set_state(FinishShiftState.cash)


@router.message(FinishShiftState.cash)
async def get_cash(message: Message, state: FSMContext):
    try:
        cash = float(message.text.replace(",", "."))

    except ValueError:
        await message.answer("Введите сумму числом.")
        return

    await state.update_data(cash=cash)
    await message.answer("Введите карту / безнал:")
    await state.set_state(FinishShiftState.card)


@router.message(FinishShiftState.card)
async def get_card(message: Message, state: FSMContext):
    try:
        card = float(message.text.replace(",", "."))

    except ValueError:
        await message.answer("Введите сумму числом.")
        return

    await state.update_data(card=card)
    await message.answer("Введите расход на зарядку:")
    await state.set_state(FinishShiftState.charging_expense)


@router.message(FinishShiftState.charging_expense)
async def get_charging_expense(message: Message, state: FSMContext):
    try:
        charging_expense = float(message.text.replace(",", "."))

    except ValueError:
        await message.answer("Введите сумму числом.")
        return

    await state.update_data(charging_expense=charging_expense)
    await message.answer("🧾 Прикрепите чек за зарядку:")
    await state.set_state(FinishShiftState.charging_receipt)


@router.message(FinishShiftState.charging_receipt)
async def get_charging_receipt(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото чека.")
        return

    await state.update_data(charging_receipt=message.photo[-1].file_id)
    await message.answer("Введите комиссию Яндекса:")
    await state.set_state(FinishShiftState.yandex_commission)


@router.message(FinishShiftState.yandex_commission)
async def get_yandex_commission(message: Message, state: FSMContext):
    try:
        yandex_commission = float(message.text.replace(",", "."))

    except ValueError:
        await message.answer("Введите сумму числом.")
        return

    data = await state.get_data()
    turnover = data["turnover"]

    recommended_salary, salary_percent = calculate_driver_salary(turnover)

    await state.update_data(
        yandex_commission=yandex_commission,
        recommended_salary=recommended_salary,
        salary_percent=salary_percent
    )

    await message.answer(
        f"🤖 Рекомендуемая зарплата водителя:\n\n"
        f"Оборот: {turnover:.0f} сом\n"
        f"Процент: {salary_percent}%\n"
        f"Рекомендуемая сумма: {recommended_salary:.0f} сом\n\n"
        f"Введите итоговую зарплату водителя:"
    )

    await state.set_state(FinishShiftState.driver_salary)


@router.message(FinishShiftState.driver_salary)
async def get_driver_salary(message: Message, state: FSMContext):
    try:
        driver_salary = float(message.text.replace(",", "."))

        if driver_salary < 0:
            await message.answer("Зарплата не может быть меньше 0.")
            return

    except ValueError:
        await message.answer("Введите сумму числом.")
        return

    await state.update_data(driver_salary=driver_salary)

    await message.answer(
        "Введите сумму штрафа водителя.\n"
        "Если штрафа нет — введите 0:"
    )

    await state.set_state(FinishShiftState.fine_amount)


@router.message(FinishShiftState.fine_amount)
async def get_fine_amount(message: Message, state: FSMContext):
    try:
        fine_amount = float(message.text.replace(",", "."))

        if fine_amount < 0:
            await message.answer("Штраф не может быть меньше 0.")
            return

    except ValueError:
        await message.answer("Введите сумму числом.")
        return

    await state.update_data(fine_amount=fine_amount)

    if fine_amount > 0:
        await message.answer("Введите причину штрафа:")
        await state.set_state(FinishShiftState.fine_reason)
    else:
        await state.update_data(fine_reason=None)

        await message.answer(
            "Введите сумму пополнения депозита водителя.\n"
            "Если пополнения нет — введите 0:"
        )

        await state.set_state(FinishShiftState.deposit_top_up)


@router.message(FinishShiftState.fine_reason)
async def get_fine_reason(message: Message, state: FSMContext):
    reason = message.text.strip()

    if not reason:
        await message.answer("Введите причину штрафа.")
        return

    await state.update_data(fine_reason=reason)

    await message.answer(
        "Введите сумму пополнения депозита водителя.\n"
        "Если пополнения нет — введите 0:"
    )

    await state.set_state(FinishShiftState.deposit_top_up)


@router.message(FinishShiftState.deposit_top_up)
async def get_deposit_top_up(message: Message, state: FSMContext):
    try:
        deposit_top_up = float(message.text.replace(",", "."))

        if deposit_top_up < 0:
            await message.answer("Сумма не может быть меньше 0.")
            return

    except ValueError:
        await message.answer("Введите сумму числом.")
        return

    await state.update_data(deposit_top_up=deposit_top_up)

    if deposit_top_up > 0:
        await message.answer("🧾 Отправьте фото чека пополнения депозита:")
        await state.set_state(FinishShiftState.deposit_receipt)
    else:
        await finish_shift_final(
            message,
            state,
            deposit_receipt=None
        )


@router.message(FinishShiftState.deposit_receipt)
async def get_deposit_receipt(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото чека депозита.")
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
    fine_amount = data.get("fine_amount", 0) or 0
    fine_reason = data.get("fine_reason")
    deposit_top_up = data["deposit_top_up"]

    driver_id = await get_shift_driver_id(shift_id)

    fine_result = None

    if driver_id and fine_amount > 0:
        fine_result = await deduct_fine_from_driver_deposit(
            driver_id=driver_id,
            shift_id=shift_id,
            amount=fine_amount,
            reason=fine_reason
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
        charging_receipt=data["charging_receipt"],
        fine_amount=fine_amount,
        fine_reason=fine_reason
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

    total_expenses = charging_expense + yandex_commission + driver_salary
    profit = turnover - total_expenses

    text = (
        "✅ Смена закрыта\n\n"
        f"Заказы: {orders_count}\n"
        f"Оборот: {turnover:.0f} сом\n"
        f"Наличка: {cash:.0f} сом\n"
        f"Карта / безнал: {card:.0f} сом\n\n"
        f"Заряд машины: {data['battery_percent']}%\n"
        f"Расход на зарядку: {charging_expense:.0f} сом\n"
        f"Комиссия Яндекса: {yandex_commission:.0f} сом\n\n"
        f"🤖 Рекомендованная зарплата: {recommended_salary:.0f} сом ({salary_percent}%)\n"
        f"💵 Фактическая зарплата: {driver_salary:.0f} сом\n\n"
    )

    if fine_amount > 0:
        text += (
            f"🚫 Штраф: {fine_amount:.0f} сом\n"
            f"Причина: {fine_reason}\n"
        )

        if fine_result:
            text += (
                f"Удержано с депозита: {fine_result['deducted_amount']:.0f} сом\n"
                f"Остаток депозита: {fine_result['new_deposit']:.0f} сом\n"
            )

            if fine_result["remaining_debt"] > 0:
                text += (
                    f"В долг добавлено: {fine_result['remaining_debt']:.0f} сом\n"
                )

        text += "\n"
    else:
        text += "🚫 Штрафа нет\n\n"

    text += (
        f"Итого расходы: {total_expenses:.0f} сом\n"
        f"Прибыль: {profit:.0f} сом\n\n"
    )

    if deposit_top_up > 0 and new_deposit is not None:
        text += (
            f"💰 Пополнение депозита: {deposit_top_up:.0f} сом\n"
            f"Текущий депозит водителя: {new_deposit:.0f} сом\n"
        )

        if new_deposit >= 20000:
            text += (
                "\n⚠️ Депозит достиг 20 000 сом.\n"
                "Накопление депозита нужно остановить."
            )
        else:
            text += (
                f"До лимита 20 000 осталось: {20000 - new_deposit:.0f} сом"
            )
    else:
        text += "💰 Пополнения депозита не было."

    await message.answer(
        text,
        reply_markup=shifts_menu_keyboard()
    )

    await state.clear()