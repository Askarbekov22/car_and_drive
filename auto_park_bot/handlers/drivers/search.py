from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.drivers import drivers_menu_keyboard
from keyboards.main import main_menu_keyboard

from services.driver_service import (
    get_all_drivers_full,
    search_drivers,
    get_driver_active_car
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


def safe_money(value):
    return float(value or 0)


def safe_text(value):
    if value is None or value == "":
        return "—"

    return str(value)


def driver_full_text(driver, active_car):
    text = (
        "🔎 Данные водителя:\n\n"
        f"ID: {driver[0]}\n"
        f"ФИО: {safe_text(driver[1])}\n"
        f"Телефон: {safe_text(driver[2])}\n"
        f"Адрес: {safe_text(driver[5])}\n"
        f"Доп. контакт 1: {safe_text(driver[6])}\n"
        f"Доп. контакт 2: {safe_text(driver[7])}\n"
        f"Дата принятия: {safe_text(driver[8])}\n"
        f"Дата создания: {safe_text(driver[21])}\n\n"
        "💰 Финансы:\n"
        f"Депозит: {safe_money(driver[10]):.0f} сом\n"
        f"Лимит депозита: {safe_money(driver[12]):.0f} сом\n"
        f"Статус депозита: {safe_text(driver[13])}\n"
        f"Доход с водителя: {safe_money(driver[15]):.0f} сом\n"
        f"Оборот: {safe_money(driver[16]):.0f} сом\n"
        f"Зарплата всего: {safe_money(driver[18]):.0f} сом\n"
        f"Долг: {safe_money(driver[19]):.0f} сом\n"
        f"Ущерб: {safe_money(driver[17]):.0f} сом\n"
        f"Штрафы: {safe_money(driver[20]):.0f} сом\n\n"
        "📊 Работа:\n"
        f"Всего заказов: {driver[14] or 0}\n"
    )

    if active_car:
        text += (
            "\n🚗 Текущая машина:\n"
            f"ID машины: {active_car[0]}\n"
            f"Госномер: {safe_text(active_car[1])}\n"
            f"Модель: {safe_text(active_car[2])}\n"
            f"Статус машины: {safe_text(active_car[3])}\n"
            f"ID смены: {active_car[4]}\n"
            f"Начало смены: {safe_text(active_car[5])}\n"
        )
    else:
        text += "\n🚗 Текущая машина: нет активной смены\n"

    return text


async def send_driver_files(message: Message, driver):
    passport_front = driver[3]
    passport_back = driver[4]
    contract_file = driver[9]
    deposit_receipt = driver[11]

    if passport_front:
        try:
            await message.answer_photo(
                passport_front,
                caption="📄 Паспорт: передняя сторона"
            )
        except Exception:
            await message.answer("⚠️ Не удалось отправить переднюю сторону паспорта.")

    if passport_back:
        try:
            await message.answer_photo(
                passport_back,
                caption="📄 Паспорт: задняя сторона"
            )
        except Exception:
            await message.answer("⚠️ Не удалось отправить заднюю сторону паспорта.")

    if contract_file:
        try:
            await message.answer_document(
                contract_file,
                caption="📑 Договор водителя"
            )
        except Exception:
            await message.answer("⚠️ Не удалось отправить договор.")

    if deposit_receipt:
        try:
            await message.answer_photo(
                deposit_receipt,
                caption="🧾 Чек депозита"
            )
        except Exception:
            await message.answer("⚠️ Не удалось отправить чек депозита.")


@router.message(lambda message: message.text == "📋 Список водителей")
async def list_drivers(message: Message):
    drivers = await get_all_drivers_full()

    if not drivers:
        await message.answer("Список водителей пуст.")
        return

    text = "📋 Список водителей:\n\n"

    for driver in drivers:
        text += (
            f"ID: {driver[0]}\n"
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

    query = message.text.strip()

    if not query:
        await message.answer("Введите ФИО или номер телефона.")
        return

    drivers = await search_drivers(query)

    if not drivers:
        await message.answer(
            "Водитель не найден.\n"
            "Введите другое ФИО или номер телефона."
        )
        return

    if len(drivers) > 5:
        await message.answer(
            f"Найдено слишком много водителей: {len(drivers)}.\n"
            "Уточните ФИО или номер телефона."
        )
        return

    for driver in drivers:
        active_car = await get_driver_active_car(driver[0])

        await message.answer(
            driver_full_text(driver, active_car),
            reply_markup=drivers_menu_keyboard()
        )

        await send_driver_files(message, driver)

    await state.clear()