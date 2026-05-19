import os

from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.accident_keyboards import accident_menu_keyboard
from services.accident_service import (
    get_accident_report,
    get_accident_report_by_dates,
)
from services.accident_excel_service import create_accident_excel

router = Router()


class AccidentReportState(StatesGroup):
    start_date = State()
    end_date = State()


def _is_valid_date(value: str) -> bool:
    return len(value) == 10 and value[4] == "-" and value[7] == "-"


@router.message(lambda message: message.text in ["Отчет ДТП", " Отчет ДТП", "📊 Отчет ДТП"])
async def accident_report(message: Message, state: FSMContext):
    await state.clear()

    report = await get_accident_report()

    total_count = report[0] or 0
    total_damage = report[1] or 0
    total_paid = report[2] or 0
    total_debt = report[3] or 0
    open_count = report[4] or 0
    closed_count = report[5] or 0
    driver_count = report[6] or 0
    company_count = report[7] or 0
    insurance_count = report[8] or 0
    mixed_count = report[9] or 0

    await message.answer(
        f"Общий отчет по ДТП:\n\n"
        f"Всего ДТП: {total_count}\n"
        f"Открытые: {open_count}\n"
        f"Закрытые: {closed_count}\n\n"
        f"Общий ущерб: {total_damage:.0f} сом\n"
        f"Оплачено: {total_paid:.0f} сом\n"
        f"Остаток долга: {total_debt:.0f} сом\n\n"
        f"Кто оплачивает:\n"
        f"Водитель: {driver_count}\n"
        f"Компания: {company_count}\n"
        f"Страховая / КАСКО: {insurance_count}\n"
        f"Смешанная: {mixed_count}\n\n"
        f"Для отчета по периоду введите дату начала в формате ГГГГ-ММ-ДД:"
    )

    await state.set_state(AccidentReportState.start_date)


@router.message(AccidentReportState.start_date)
async def accident_report_start_date(message: Message, state: FSMContext):
    start_date = message.text.strip()

    if not _is_valid_date(start_date):
        await message.answer("Неверный формат.\nНапример: 2026-05-01")
        return

    await state.update_data(start_date=start_date)
    await message.answer("Введите дату конца в формате ГГГГ-ММ-ДД:")
    await state.set_state(AccidentReportState.end_date)


@router.message(AccidentReportState.end_date)
async def accident_report_end_date(message: Message, state: FSMContext):
    end_date = message.text.strip()

    if not _is_valid_date(end_date):
        await message.answer("Неверный формат.\nНапример: 2026-05-31")
        return

    data = await state.get_data()
    start_date = data["start_date"]

    report = await get_accident_report_by_dates(start_date, end_date)

    total_count = report[0] or 0
    total_damage = report[1] or 0
    total_paid = report[2] or 0
    total_debt = report[3] or 0
    open_count = report[4] or 0
    closed_count = report[5] or 0

    await message.answer(
        f"Отчет ДТП за период:\n"
        f"{start_date} — {end_date}\n\n"
        f"Всего ДТП: {total_count}\n"
        f"Открытые: {open_count}\n"
        f"Закрытые: {closed_count}\n\n"
        f"Общий ущерб: {total_damage:.0f} сом\n"
        f"Оплачено: {total_paid:.0f} сом\n"
        f"Остаток долга: {total_debt:.0f} сом",
        reply_markup=accident_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "📊 Скачать Excel ДТП")
async def download_accident_excel(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Генерирую Excel по ДТП...")

    try:
        file_path = await create_accident_excel()

        document = FSInputFile(
            file_path,
            filename="ДТП Машин.xlsx"
        )

        await message.answer_document(
            document=document,
            caption="📊 Excel отчет по ДТП",
            reply_markup=accident_menu_keyboard()
        )

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as error:
        await message.answer(
            f"Не удалось создать Excel ДТП.\n\nОшибка: {error}",
            reply_markup=accident_menu_keyboard()
        )