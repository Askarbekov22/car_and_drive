from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.accident_keyboards import (
    accident_menu_keyboard,
    payment_type_keyboard,
    accident_list_keyboard,
    edit_accident_fields_keyboard,
    edit_payment_type_keyboard
)
from keyboards.main import main_menu_keyboard

from services.accident_service import (
    create_accident,
    get_all_accidents,
    close_accident,
    get_accident_by_id,
    update_accident_field,
    get_accident_report,
    get_accident_report_by_dates
)
from services.shift_service import get_shift_full_by_id

router = Router()


class AccidentState(StatesGroup):
    shift_id = State()
    accident_date = State()
    damage_amount = State()
    payment_type = State()
    paid_amount = State()
    photo_1 = State()
    photo_2 = State()
    note = State()


class EditAccidentState(StatesGroup):
    accident_id = State()
    field_name = State()
    new_value = State()


class AccidentReportState(StatesGroup):
    start_date = State()
    end_date = State()


@router.message(F.text == "🚨 ДТП")
async def accidents_menu(message: Message):
    await message.answer(
        "Раздел ДТП 🚨",
        reply_markup=accident_menu_keyboard()
    )


@router.message(F.text == "⬅️ Главное меню")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard()
    )


@router.message(F.text == "➕ Добавить ДТП")
async def start_add_accident(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AccidentState.shift_id)
    await message.answer("Введите ID смены:")


@router.message(AccidentState.shift_id)
async def get_accident_shift_id(message: Message, state: FSMContext):
    try:
        shift_id = int(message.text)
    except ValueError:
        await message.answer("Введите ID смены цифрами.")
        return

    shift = await get_shift_full_by_id(shift_id)

    if not shift:
        await message.answer("Смена не найдена. Проверь ID смены.")
        return

    await state.update_data(shift_id=shift_id)
    await state.set_state(AccidentState.accident_date)

    await message.answer(
        f"Смена найдена:\n\n"
        f"Водитель: {shift['driver_name']}\n"
        f"Машина: {shift['plate_number']} {shift['car_model']}\n"
        f"Статус смены: {shift['status']}\n\n"
        f"Введите дату ДТП в формате ГГГГ-ММ-ДД:\n"
        f"Например: 2026-05-14"
    )


@router.message(AccidentState.accident_date)
async def get_accident_date(message: Message, state: FSMContext):
    accident_date = message.text.strip()

    if len(accident_date) != 10 or accident_date[4] != "-" or accident_date[7] != "-":
        await message.answer("Неверный формат. Введите дату так: 2026-05-14")
        return

    await state.update_data(accident_date=accident_date)
    await state.set_state(AccidentState.damage_amount)

    await message.answer("Введите сумму ущерба:")


@router.message(AccidentState.damage_amount)
async def get_damage_amount(message: Message, state: FSMContext):
    try:
        damage_amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите сумму ущерба цифрами.")
        return

    if damage_amount < 0:
        await message.answer("Сумма ущерба не может быть меньше нуля.")
        return

    await state.update_data(damage_amount=damage_amount)
    await state.set_state(AccidentState.payment_type)

    await message.answer(
        "Кто оплачивает ДТП?",
        reply_markup=payment_type_keyboard()
    )


@router.callback_query(AccidentState.payment_type, F.data.startswith("accident_payment_"))
async def get_payment_type(callback: CallbackQuery, state: FSMContext):
    payment_type = callback.data.replace("accident_payment_", "")

    payment_names = {
        "driver": "Водитель",
        "company": "Компания",
        "insurance": "Страховая",
        "mixed": "Смешанная оплата"
    }

    await state.update_data(payment_type=payment_type)
    await state.set_state(AccidentState.paid_amount)

    await callback.message.answer(
        f"Выбрано: {payment_names.get(payment_type, payment_type)}\n\n"
        f"Введите уже оплаченную сумму:"
    )

    await callback.answer()


@router.message(AccidentState.paid_amount)
async def get_paid_amount(message: Message, state: FSMContext):
    try:
        paid_amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите оплаченную сумму цифрами.")
        return

    if paid_amount < 0:
        await message.answer("Оплаченная сумма не может быть меньше нуля.")
        return

    await state.update_data(paid_amount=paid_amount)
    await state.set_state(AccidentState.photo_1)

    await message.answer("Отправьте первое фото ДТП:")


@router.message(AccidentState.photo_1, F.photo)
async def get_photo_1(message: Message, state: FSMContext):
    photo_1 = message.photo[-1].file_id

    await state.update_data(photo_1=photo_1)
    await state.set_state(AccidentState.photo_2)

    await message.answer("Отправьте второе фото ДТП:")


@router.message(AccidentState.photo_1)
async def wrong_photo_1(message: Message):
    await message.answer("Нужно отправить фото, не текст.")


@router.message(AccidentState.photo_2, F.photo)
async def get_photo_2(message: Message, state: FSMContext):
    photo_2 = message.photo[-1].file_id

    await state.update_data(photo_2=photo_2)
    await state.set_state(AccidentState.note)

    await message.answer("Введите заметку по ДТП:")


@router.message(AccidentState.photo_2)
async def wrong_photo_2(message: Message):
    await message.answer("Нужно отправить фото, не текст.")


@router.message(AccidentState.note)
async def finish_add_accident(message: Message, state: FSMContext):
    data = await state.get_data()

    accident_id = await create_accident(
        shift_id=data["shift_id"],
        accident_date=data["accident_date"],
        damage_amount=data["damage_amount"],
        payment_type=data["payment_type"],
        paid_amount=data["paid_amount"],
        photo_1=data["photo_1"],
        photo_2=data["photo_2"],
        note=message.text
    )

    if not accident_id:
        await message.answer(
            "Не удалось создать ДТП. Проверь данные.",
            reply_markup=accident_menu_keyboard()
        )
        await state.clear()
        return

    debt_amount = data["damage_amount"] - data["paid_amount"]

    if debt_amount < 0:
        debt_amount = 0

    await message.answer(
        f"✅ ДТП #{accident_id} добавлено.\n\n"
        f"Дата ДТП: {data['accident_date']}\n"
        f"Сумма ущерба: {data['damage_amount']} сом\n"
        f"Оплачено: {data['paid_amount']} сом\n"
        f"Остаток: {debt_amount} сом\n\n"
        f"Машина переведена в статус repair.",
        reply_markup=accident_menu_keyboard()
    )

    await state.clear()


@router.message(F.text == "📋 Список ДТП")
async def list_accidents(message: Message):
    accidents = await get_all_accidents()

    if not accidents:
        await message.answer("ДТП пока нет.")
        return

    payment_names = {
        "driver": "Водитель",
        "company": "Компания",
        "insurance": "Страховая",
        "mixed": "Смешанная оплата"
    }

    text = "📋 Список ДТП:\n\n"

    for accident in accidents:
        text += (
            f"🚨 ДТП #{accident[0]}\n"
            f"Смена: {accident[1]}\n"
            f"Водитель: {accident[2]}\n"
            f"Машина: {accident[3]} {accident[4]}\n"
            f"Дата ДТП: {accident[5]}\n"
            f"Ущерб: {accident[6]} сом\n"
            f"Оплачивает: {payment_names.get(accident[7], accident[7])}\n"
            f"Оплачено: {accident[8]} сом\n"
            f"Остаток: {accident[9]} сом\n"
            f"Заметка: {accident[10]}\n"
            f"Создано: {accident[11]}\n"
            f"Статус: {accident[12]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=accident_list_keyboard(accidents)
    )


@router.message(F.text == "✏️ Редактировать ДТП")
async def edit_accident_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(EditAccidentState.accident_id)
    await message.answer("Введите ID ДТП, которое нужно редактировать:")


@router.message(EditAccidentState.accident_id)
async def edit_accident_get_id(message: Message, state: FSMContext):
    try:
        accident_id = int(message.text)
    except ValueError:
        await message.answer("Введите ID ДТП цифрами.")
        return

    accident = await get_accident_by_id(accident_id)

    if not accident:
        await message.answer("ДТП не найдено.")
        return

    await state.clear()

    await message.answer(
        f"Выберите, что редактировать в ДТП #{accident_id}:",
        reply_markup=edit_accident_fields_keyboard(accident_id)
    )


@router.callback_query(F.data.startswith("edit_accident_"))
async def edit_accident_choose_field(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    parts = data.split("_")
    accident_id = int(parts[-1])

    if "date" in data:
        field_name = "accident_date"
        text = "Введите новую дату ДТП в формате ГГГГ-ММ-ДД:"
    elif "damage" in data:
        field_name = "damage_amount"
        text = "Введите новую сумму ущерба:"
    elif "payment_type" in data:
        await callback.message.answer(
            "Выберите новый тип оплаты:",
            reply_markup=edit_payment_type_keyboard(accident_id)
        )
        await callback.answer()
        return
    elif "paid" in data:
        field_name = "paid_amount"
        text = "Введите новую оплаченную сумму:"
    elif "note" in data:
        field_name = "note"
        text = "Введите новую заметку:"
    else:
        await callback.answer()
        return

    await state.update_data(
        accident_id=accident_id,
        field_name=field_name
    )

    await state.set_state(EditAccidentState.new_value)

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data.startswith("set_payment_"))
async def set_new_payment_type(callback: CallbackQuery):
    data = callback.data.replace("set_payment_", "")
    parts = data.split("_")

    payment_type = parts[0]
    accident_id = int(parts[1])

    result = await update_accident_field(
        accident_id=accident_id,
        field_name="payment_type",
        value=payment_type
    )

    if not result:
        await callback.message.answer("Не удалось обновить тип оплаты.")
        await callback.answer()
        return

    await callback.message.answer(
        f"✅ Тип оплаты ДТП #{accident_id} обновлен.",
        reply_markup=accident_menu_keyboard()
    )

    await callback.answer()


@router.message(EditAccidentState.new_value)
async def edit_accident_save_value(message: Message, state: FSMContext):
    data = await state.get_data()

    accident_id = data["accident_id"]
    field_name = data["field_name"]
    value = message.text.strip()

    if field_name in ["damage_amount", "paid_amount"]:
        try:
            value = float(value.replace(",", "."))
        except ValueError:
            await message.answer("Введите сумму цифрами.")
            return

        if value < 0:
            await message.answer("Сумма не может быть меньше нуля.")
            return

    if field_name == "accident_date":
        if len(value) != 10 or value[4] != "-" or value[7] != "-":
            await message.answer("Неверный формат. Введите дату так: 2026-05-14")
            return

    result = await update_accident_field(
        accident_id=accident_id,
        field_name=field_name,
        value=value
    )

    if not result:
        await message.answer("Не удалось обновить ДТП.")
        await state.clear()
        return

    await message.answer(
        f"✅ ДТП #{accident_id} обновлено.",
        reply_markup=accident_menu_keyboard()
    )

    await state.clear()


@router.message(F.text == "📊 Отчет ДТП")
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
        f"📊 Общий отчет по ДТП:\n\n"
        f"Всего ДТП: {total_count}\n"
        f"Открытые: {open_count}\n"
        f"Закрытые: {closed_count}\n\n"
        f"Общий ущерб: {total_damage} сом\n"
        f"Оплачено: {total_paid} сом\n"
        f"Остаток долга: {total_debt} сом\n\n"
        f"Кто оплачивает:\n"
        f"Водитель: {driver_count}\n"
        f"Компания: {company_count}\n"
        f"Страховая: {insurance_count}\n"
        f"Смешанная: {mixed_count}\n\n"
        f"Для отчета по периоду введите дату начала в формате ГГГГ-ММ-ДД:"
    )

    await state.set_state(AccidentReportState.start_date)


@router.message(AccidentReportState.start_date)
async def accident_report_start_date(message: Message, state: FSMContext):
    start_date = message.text.strip()

    if len(start_date) != 10 or start_date[4] != "-" or start_date[7] != "-":
        await message.answer("Неверный формат. Введите дату так: 2026-05-01")
        return

    await state.update_data(start_date=start_date)
    await state.set_state(AccidentReportState.end_date)

    await message.answer("Введите дату конца в формате ГГГГ-ММ-ДД:")


@router.message(AccidentReportState.end_date)
async def accident_report_end_date(message: Message, state: FSMContext):
    end_date = message.text.strip()

    if len(end_date) != 10 or end_date[4] != "-" or end_date[7] != "-":
        await message.answer("Неверный формат. Введите дату так: 2026-05-31")
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
        f"📊 Отчет ДТП за период:\n"
        f"{start_date} — {end_date}\n\n"
        f"Всего ДТП: {total_count}\n"
        f"Открытые: {open_count}\n"
        f"Закрытые: {closed_count}\n\n"
        f"Общий ущерб: {total_damage} сом\n"
        f"Оплачено: {total_paid} сом\n"
        f"Остаток долга: {total_debt} сом",
        reply_markup=accident_menu_keyboard()
    )

    await state.clear()


@router.callback_query(F.data.startswith("close_accident_"))
async def close_accident_callback(callback: CallbackQuery):
    accident_id = int(callback.data.replace("close_accident_", ""))

    result = await close_accident(accident_id)

    if not result:
        await callback.message.answer("ДТП не найдено.")
        await callback.answer()
        return

    await callback.message.answer(
        f"✅ ДТП #{accident_id} закрыто.\n"
        f"Машина переведена в статус free.",
        reply_markup=accident_menu_keyboard()
    )

    await callback.answer()