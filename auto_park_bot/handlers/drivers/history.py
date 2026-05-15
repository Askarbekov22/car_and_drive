from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.drivers import drivers_menu_keyboard
from keyboards.main import main_menu_keyboard

from services.driver_service import (
    search_drivers,
    get_driver_shift_history,
    get_driver_income_history,
    get_driver_income_summary,
    get_driver_fines
)

router = Router()


class DriverHistoryState(StatesGroup):
    shift_history_driver = State()
    income_history_driver = State()
    fines_history_driver = State()


async def back_to_main(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard(message.from_user.id)
    )


@router.message(lambda message: message.text == "🕘 История смен водителя")
async def start_driver_shift_history(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ФИО или номер телефона:")
    await state.set_state(DriverHistoryState.shift_history_driver)


@router.message(DriverHistoryState.shift_history_driver)
async def show_driver_shift_history(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
        return

    drivers = await search_drivers(message.text.strip())

    if not drivers:
        await message.answer(
            "Водитель не найден.\n"
            "Введите другое ФИО или номер телефона."
        )
        return

    driver = drivers[0]
    shifts = await get_driver_shift_history(driver[0])

    if not shifts:
        await message.answer(
            f"У водителя {driver[1]} пока нет смен.",
            reply_markup=drivers_menu_keyboard()
        )
        await state.clear()
        return

    text = (
        f"🕘 История смен водителя\n\n"
        f"Водитель: {driver[1]}\n\n"
    )

    for shift in shifts:
        text += (
            f"Смена #{shift[0]}\n"
            f"Машина: {shift[1]} {shift[2]}\n"
            f"Заказы: {shift[3] or 0}\n"
            f"Оборот: {shift[4] or 0:.0f} сом\n"
            f"Зарплата: {shift[5] or 0:.0f} сом\n"
            f"Зарядка: {shift[6] or 0:.0f} сом\n"
            f"Комиссия Яндекса: {shift[7] or 0:.0f} сом\n"
            f"Заряд машины: {shift[8] or 0}%\n"
            f"Штраф: {shift[11] or 0:.0f} сом\n"
            f"Причина штрафа: {shift[12] or '-'}\n"
            f"Начало: {shift[9]}\n"
            f"Конец: {shift[10]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "💰 История дохода водителя")
async def start_driver_income_history(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ФИО или номер телефона:")
    await state.set_state(DriverHistoryState.income_history_driver)


@router.message(DriverHistoryState.income_history_driver)
async def show_driver_income_history(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
        return

    drivers = await search_drivers(message.text.strip())

    if not drivers:
        await message.answer(
            "Водитель не найден.\n"
            "Введите другое ФИО или номер телефона."
        )
        return

    driver = drivers[0]

    summary = await get_driver_income_summary(driver[0])
    income_history = await get_driver_income_history(driver[0])

    text = (
        f"💰 История дохода водителя\n\n"
        f"Водитель: {driver[1]}\n\n"
        f"Всего смен: {summary[0] or 0}\n"
        f"Всего заказов: {summary[1] or 0}\n"
        f"Общий оборот: {summary[2] or 0:.0f} сом\n"
        f"Общая зарплата: {summary[3] or 0:.0f} сом\n"
        f"Средний оборот: {summary[4] or 0:.0f} сом\n"
        f"Средняя зарплата: {summary[5] or 0:.0f} сом\n"
        f"Всего штрафов: {summary[6] or 0:.0f} сом\n\n"
        f"Последние смены:\n\n"
    )

    for row in income_history:
        text += (
            f"Смена #{row[0]}\n"
            f"Оборот: {row[1] or 0:.0f} сом\n"
            f"Фактическая зарплата: {row[2] or 0:.0f} сом\n"
            f"Процент: {row[3] or 0}%\n"
            f"Рекомендовано: {row[4] or 0:.0f} сом\n"
            f"Штраф: {row[6] or 0:.0f} сом\n"
            f"Причина: {row[7] or '-'}\n"
            f"Дата: {row[5]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "🚫 История штрафов водителя")
async def start_driver_fines_history(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ФИО или номер телефона:")
    await state.set_state(DriverHistoryState.fines_history_driver)


@router.message(DriverHistoryState.fines_history_driver)
async def show_driver_fines_history(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
        return

    drivers = await search_drivers(message.text.strip())

    if not drivers:
        await message.answer(
            "Водитель не найден.\n"
            "Введите другое ФИО или номер телефона."
        )
        return

    driver = drivers[0]
    fines = await get_driver_fines(driver[0])

    if not fines:
        await message.answer(
            f"У водителя {driver[1]} пока нет штрафов.",
            reply_markup=drivers_menu_keyboard()
        )
        await state.clear()
        return

    text = (
        f"🚫 История штрафов\n\n"
        f"Водитель: {driver[1]}\n\n"
    )

    for fine in fines:
        text += (
            f"Штраф #{fine[0]}\n"
            f"Смена: {fine[1]}\n"
            f"Сумма: {fine[2] or 0:.0f} сом\n"
            f"Причина: {fine[3]}\n"
            f"Удержано с депозита: {fine[4] or 0:.0f} сом\n"
            f"Добавлено в долг: {fine[5] or 0:.0f} сом\n"
            f"Дата: {fine[6]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()