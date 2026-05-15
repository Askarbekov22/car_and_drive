from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.drivers import drivers_menu_keyboard
from keyboards.main import main_menu_keyboard

from services.driver_service import (
    get_all_drivers_full,
    search_drivers
)

router = Router()


class DriverSearchState(StatesGroup):
    search_query = State()


async def back_to_main(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard(message.from_user.id)
    )


@router.message(lambda message: message.text == "📋 Список водителей")
async def list_drivers(message: Message):
    drivers = await get_all_drivers_full()

    if not drivers:
        await message.answer("Список водителей пуст.")
        return

    text = "📋 Список водителей:\n\n"

    for driver in drivers:
        text += (
            f"ФИО: {driver[1]}\n"
            f"Телефон: {driver[2]}\n"
            f"Депозит: {driver[3] or 0:.0f} сом\n"
            f"Статус депозита: {driver[4]}\n"
            f"Заказы: {driver[5] or 0}\n"
            f"Оборот: {driver[7] or 0:.0f} сом\n"
            f"Зарплата: {driver[9] or 0:.0f} сом\n"
            f"Долг: {driver[10] or 0:.0f} сом\n"
            f"Штрафы: {driver[11] or 0:.0f} сом\n\n"
        )

    await message.answer(text)


@router.message(lambda message: message.text == "🔎 Поиск водителя")
async def start_driver_search(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ФИО или номер телефона:")
    await state.set_state(DriverSearchState.search_query)


@router.message(DriverSearchState.search_query)
async def process_driver_search(message: Message, state: FSMContext):
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

    text = "🔎 Результаты поиска:\n\n"

    for driver in drivers:
        text += (
            f"ФИО: {driver[1]}\n"
            f"Телефон: {driver[2]}\n"
            f"Депозит: {driver[3] or 0:.0f} сом\n"
            f"Статус депозита: {driver[4]}\n"
            f"Заказы: {driver[5] or 0}\n"
            f"Оборот: {driver[7] or 0:.0f} сом\n"
            f"Зарплата: {driver[9] or 0:.0f} сом\n"
            f"Долг: {driver[10] or 0:.0f} сом\n"
            f"Штрафы: {driver[11] or 0:.0f} сом\n\n"
        )

    await message.answer(
        text,
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()