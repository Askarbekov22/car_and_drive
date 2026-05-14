from datetime import datetime, timedelta

from aiogram import Router
from aiogram.types import Message, FSInputFile

from keyboards.reports import reports_keyboard, finished_shifts_keyboard
from keyboards.main import main_menu_keyboard
from services.shift_service import (
    get_finished_shifts,
    get_shift_by_id,
    get_shifts_by_period,
    get_active_shifts
)
from services.excel_service import create_full_excel_report

router = Router()


def get_today():
    return datetime.now().date()


def get_yesterday():
    return get_today() - timedelta(days=1)


def get_current_week():
    today = get_today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_current_month():
    today = get_today()
    start = today.replace(day=1)
    end = today
    return start, end


@router.message(lambda message: message.text == "📊 Отчёты")
async def reports_menu(message: Message):
    await message.answer(
        "Выберите отчёт:",
        reply_markup=reports_keyboard()
    )


@router.message(lambda message: message.text == "🔄 Актуальные смены")
async def active_shifts_report(message: Message):
    shifts = await get_active_shifts()

    if not shifts:
        await message.answer("Актуальных смен нет.")
        return

    text = "🔄 Актуальные смены\n\n"

    for shift in shifts:
        text += (
            f"Смена #{shift[0]}\n"
            f"Водитель: {shift[1]}\n"
            f"Машина: {shift[2]} | {shift[3]}\n\n"
        )

    await message.answer(text)


@router.message(lambda message: message.text == "📅 Сегодня")
async def report_today(message: Message):
    today = get_today()
    await send_period_report(
        message,
        today.strftime("%Y-%m-%d"),
        today.strftime("%Y-%m-%d"),
        "📅 Отчёт за сегодня"
    )


@router.message(lambda message: message.text == "📅 Вчера")
async def report_yesterday(message: Message):
    yesterday = get_yesterday()
    await send_period_report(
        message,
        yesterday.strftime("%Y-%m-%d"),
        yesterday.strftime("%Y-%m-%d"),
        "📅 Отчёт за вчера"
    )


@router.message(lambda message: message.text == "📅 Текущая неделя")
async def report_current_week(message: Message):
    start, end = get_current_week()
    await send_period_report(
        message,
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
        "📅 Отчёт за текущую неделю"
    )


@router.message(lambda message: message.text == "📅 Текущий месяц")
async def report_current_month(message: Message):
    start, end = get_current_month()
    await send_period_report(
        message,
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
        "📅 Отчёт за текущий месяц"
    )


@router.message(lambda message: message.text == "📊 Скачать Excel")
async def download_excel_report(message: Message):
    filepath = await create_full_excel_report()

    await message.answer_document(
        FSInputFile(filepath),
        caption="📊 Excel отчёт: сегодня / вчера / текущая неделя / текущий месяц"
    )


@router.message(lambda message: message.text == "🧾 Последние смены")
async def last_shifts(message: Message):
    shifts = await get_finished_shifts()

    if not shifts:
        await message.answer("Завершённых смен пока нет.")
        return

    await message.answer(
        "Выберите смену:",
        reply_markup=finished_shifts_keyboard(shifts)
    )


async def send_period_report(message: Message, start_date: str, end_date: str, title: str):
    shifts = await get_shifts_by_period(start_date, end_date)

    if not shifts:
        await message.answer("За этот период завершённых смен нет.")
        return

    total_orders = 0
    total_turnover = 0
    total_charging = 0
    total_yandex = 0
    total_salary = 0

    text = f"{title}\n"
    text += f"Период: {start_date} — {end_date}\n\n"

    for shift in shifts:
        shift_id = shift[0]
        driver_name = shift[1]
        plate_number = shift[2]
        orders_count = shift[3] or 0
        turnover = shift[4] or 0
        charging = shift[5] or 0
        yandex = shift[6] or 0
        salary = shift[7] or 0
        end_time = shift[8]

        expenses = charging + yandex + salary
        profit = turnover - expenses

        total_orders += orders_count
        total_turnover += turnover
        total_charging += charging
        total_yandex += yandex
        total_salary += salary

        text += (
            f"#{shift_id} | {driver_name} | {plate_number}\n"
            f"Заказы: {orders_count}\n"
            f"Оборот: {turnover:.0f} сом | Прибыль: {profit:.0f} сом\n"
            f"Закрытие: {end_time}\n\n"
        )

    total_expenses = total_charging + total_yandex + total_salary
    total_profit = total_turnover - total_expenses

    text += (
        "ИТОГО:\n"
        f"Смен: {len(shifts)}\n"
        f"Заказы: {total_orders}\n"
        f"Оборот: {total_turnover:.0f} сом\n"
        f"Расход на зарядку: {total_charging:.0f} сом\n"
        f"Комиссия Яндекса: {total_yandex:.0f} сом\n"
        f"Зарплата водителей 30%: {total_salary:.0f} сом\n"
        f"Все расходы: {total_expenses:.0f} сом\n"
        f"Прибыль: {total_profit:.0f} сом"
    )

    await message.answer(text)


@router.message(lambda message: message.text and message.text.startswith("🧾 Смена #"))
async def show_shift_by_button(message: Message):
    try:
        shift_id_text = message.text.split("|")[0].replace("🧾 Смена #", "").strip()
        shift_id = int(shift_id_text)
    except ValueError:
        await message.answer("Не смог определить смену.")
        return

    await send_shift_details(message, shift_id)


@router.message(lambda message: message.text and message.text.lower().startswith("смена "))
async def show_shift_by_text(message: Message):
    try:
        shift_id = int(message.text.lower().replace("смена", "").strip())
    except ValueError:
        await message.answer("Напиши так: смена 1")
        return

    await send_shift_details(message, shift_id)


async def send_shift_details(message: Message, shift_id: int):
    shift = await get_shift_by_id(shift_id)

    if not shift:
        await message.answer("Смена не найдена.")
        return

    turnover = shift[5] or 0
    charging = shift[8] or 0
    yandex = shift[9] or 0
    salary = shift[10] or 0

    expenses = charging + yandex + salary
    profit = turnover - expenses

    await message.answer(
        f"🧾 Смена #{shift[0]}\n\n"
        f"Водитель: {shift[1]}\n"
        f"Машина: {shift[2]} | {shift[3]}\n\n"
        f"Заказы: {shift[4] or 0}\n"
        f"Оборот: {turnover:.0f} сом\n"
        f"Наличка: {shift[6] or 0:.0f} сом\n"
        f"Карта / безнал: {shift[7] or 0:.0f} сом\n\n"
        f"Заряд машины: {shift[11] or 0}%\n"
        f"Расход на зарядку: {charging:.0f} сом\n"
        f"Комиссия Яндекса: {yandex:.0f} сом\n"
        f"Зарплата водителя 30%: {salary:.0f} сом\n\n"
        f"Расходы: {expenses:.0f} сом\n"
        f"Прибыль: {profit:.0f} сом\n\n"
        f"Начало: {shift[12]}\n"
        f"Закрытие: {shift[13]}"
    )

    await message.answer("📸 ДО НАЧАЛА СМЕНЫ")

    start_photos = [
        ("Перед", shift[14]),
        ("Зад", shift[15]),
        ("Левая", shift[16]),
        ("Правая", shift[17]),
    ]

    for name, file_id in start_photos:
        if file_id:
            await message.answer_photo(file_id, caption=name)

    await message.answer("📸 ПОСЛЕ СМЕНЫ")

    end_photos = [
        ("Перед", shift[18]),
        ("Зад", shift[19]),
        ("Левая", shift[20]),
        ("Правая", shift[21]),
    ]

    for name, file_id in end_photos:
        if file_id:
            await message.answer_photo(file_id, caption=name)

    if shift[22]:
        await message.answer_photo(shift[22], caption="🧾 Чек зарядки")


@router.message(lambda message: message.text == "⬅️ Назад")
async def back_to_main(message: Message):
    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard()
    )