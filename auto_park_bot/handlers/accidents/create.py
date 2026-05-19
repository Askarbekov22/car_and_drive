from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.accident_keyboards import (
    accident_menu_keyboard,
    payment_type_keyboard,
)
from services.accident_service import create_accident
from services.shift_service import get_shift_full_by_id

router = Router()


class AccidentState(StatesGroup):
    shift_id = State()
    accident_date = State()
    accident_place = State()
    accident_type = State()
    guilty_party = State()
    repair_fact = State()
    estimate_amount = State()
    payment_type = State()
    paid_amount = State()
    downtime_shifts = State()
    losses_amount = State()
    photo_1 = State()
    photo_2 = State()
    note = State()


def _is_valid_date(value: str) -> bool:
    return len(value) == 10 and value[4] == "-" and value[7] == "-"


def _to_float(value: str):
    return float(value.replace(",", ".").strip())


def _to_int(value: str):
    return int(value.strip())


@router.message(lambda message: message.text == "➕ Добавить ДТП")
async def start_add_accident(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите ID смены:")
    await state.set_state(AccidentState.shift_id)


@router.message(AccidentState.shift_id)
async def get_accident_shift_id(message: Message, state: FSMContext):
    if message.text == "⬅️ Главное меню":
        await state.clear()
        return

    try:
        shift_id = int(message.text)
    except ValueError:
        await message.answer("Введите ID смены цифрами.")
        return

    shift = await get_shift_full_by_id(shift_id)

    if not shift:
        await message.answer("Смена не найдена.\nПроверь ID смены.")
        return

    await state.update_data(shift_id=shift_id)

    await message.answer(
        f"Смена найдена:\n\n"
        f"Водитель: {shift['driver_name']}\n"
        f"Машина: {shift['plate_number']} {shift['car_model']}\n"
        f"Статус смены: {shift['status']}\n\n"
        f"Введите дату ДТП в формате ГГГГ-ММ-ДД:"
    )

    await state.set_state(AccidentState.accident_date)


@router.message(AccidentState.accident_date)
async def get_accident_date(message: Message, state: FSMContext):
    accident_date = message.text.strip()

    if not _is_valid_date(accident_date):
        await message.answer("Неверный формат.\nНапример: 2026-05-14")
        return

    await state.update_data(accident_date=accident_date)
    await message.answer("Введите место ДТП:\nНапример: Элебаева / Горького")
    await state.set_state(AccidentState.accident_place)


@router.message(AccidentState.accident_place)
async def get_accident_place(message: Message, state: FSMContext):
    accident_place = message.text.strip()

    if not accident_place:
        await message.answer("Место ДТП не может быть пустым.")
        return

    await state.update_data(accident_place=accident_place)
    await message.answer("Введите тип ДТП:\nНапример: среднее, морда, правая часть, сильное")
    await state.set_state(AccidentState.accident_type)


@router.message(AccidentState.accident_type)
async def get_accident_type(message: Message, state: FSMContext):
    accident_type = message.text.strip()

    if not accident_type:
        await message.answer("Тип ДТП не может быть пустым.")
        return

    await state.update_data(accident_type=accident_type)
    await message.answer("Кто виновен?\nНапример: прав / не прав / частично")
    await state.set_state(AccidentState.guilty_party)


@router.message(AccidentState.guilty_party)
async def get_guilty_party(message: Message, state: FSMContext):
    guilty_party = message.text.strip()

    if not guilty_party:
        await message.answer("Поле 'Кто виновен' не может быть пустым.")
        return

    await state.update_data(guilty_party=guilty_party)
    await message.answer("Введите факт ремонта:\nЕсли ремонта ещё не было — введите 0")
    await state.set_state(AccidentState.repair_fact)


@router.message(AccidentState.repair_fact)
async def get_repair_fact(message: Message, state: FSMContext):
    try:
        repair_fact = _to_float(message.text)
    except ValueError:
        await message.answer("Введите сумму цифрами.")
        return

    if repair_fact < 0:
        await message.answer("Сумма не может быть меньше нуля.")
        return

    await state.update_data(repair_fact=repair_fact)
    await message.answer("Введите оценку ущерба:")
    await state.set_state(AccidentState.estimate_amount)


@router.message(AccidentState.estimate_amount)
async def get_estimate_amount(message: Message, state: FSMContext):
    try:
        estimate_amount = _to_float(message.text)
    except ValueError:
        await message.answer("Введите оценку цифрами.")
        return

    if estimate_amount < 0:
        await message.answer("Оценка не может быть меньше нуля.")
        return

    await state.update_data(estimate_amount=estimate_amount)

    await message.answer(
        "Кто оплачивает ДТП?",
        reply_markup=payment_type_keyboard()
    )

    await state.set_state(AccidentState.payment_type)


@router.callback_query(AccidentState.payment_type, F.data.startswith("accident_payment_"))
async def get_payment_type(callback: CallbackQuery, state: FSMContext):
    payment_type = callback.data.replace("accident_payment_", "")

    payment_names = {
        "driver": "Водитель",
        "company": "Компания",
        "insurance": "Страховая / КАСКО",
        "mixed": "Смешанная оплата",
    }

    await state.update_data(payment_type=payment_type)

    await callback.message.answer(
        f"Выбрано: {payment_names.get(payment_type, payment_type)}\n\n"
        f"Введите уже оплаченную сумму:"
    )

    await state.set_state(AccidentState.paid_amount)
    await callback.answer()


@router.message(AccidentState.paid_amount)
async def get_paid_amount(message: Message, state: FSMContext):
    try:
        paid_amount = _to_float(message.text)
    except ValueError:
        await message.answer("Введите оплаченную сумму цифрами.")
        return

    if paid_amount < 0:
        await message.answer("Оплаченная сумма не может быть меньше нуля.")
        return

    await state.update_data(paid_amount=paid_amount)
    await message.answer("Введите простой в сменах:\nЕсли простоя нет — введите 0")
    await state.set_state(AccidentState.downtime_shifts)


@router.message(AccidentState.downtime_shifts)
async def get_downtime_shifts(message: Message, state: FSMContext):
    try:
        downtime_shifts = _to_int(message.text)
    except ValueError:
        await message.answer("Введите количество смен цифрами.")
        return

    if downtime_shifts < 0:
        await message.answer("Простой не может быть меньше нуля.")
        return

    await state.update_data(downtime_shifts=downtime_shifts)
    await message.answer("Введите потери:\nЕсли потерь нет — введите 0")
    await state.set_state(AccidentState.losses_amount)


@router.message(AccidentState.losses_amount)
async def get_losses_amount(message: Message, state: FSMContext):
    try:
        losses_amount = _to_float(message.text)
    except ValueError:
        await message.answer("Введите сумму потерь цифрами.")
        return

    if losses_amount < 0:
        await message.answer("Потери не могут быть меньше нуля.")
        return

    await state.update_data(losses_amount=losses_amount)
    await message.answer("Отправьте первое фото ДТП:")
    await state.set_state(AccidentState.photo_1)


@router.message(AccidentState.photo_1, F.photo)
async def get_photo_1(message: Message, state: FSMContext):
    await state.update_data(photo_1=message.photo[-1].file_id)
    await message.answer("Отправьте второе фото ДТП:")
    await state.set_state(AccidentState.photo_2)


@router.message(AccidentState.photo_1)
async def wrong_photo_1(message: Message):
    await message.answer("Нужно отправить фото, не текст.")


@router.message(AccidentState.photo_2, F.photo)
async def get_photo_2(message: Message, state: FSMContext):
    await state.update_data(photo_2=message.photo[-1].file_id)
    await message.answer("Введите заметку по ДТП:")
    await state.set_state(AccidentState.note)


@router.message(AccidentState.photo_2)
async def wrong_photo_2(message: Message):
    await message.answer("Нужно отправить фото, не текст.")


@router.message(AccidentState.note)
async def finish_add_accident(message: Message, state: FSMContext):
    data = await state.get_data()

    note = message.text.strip()

    repair_fact = data["repair_fact"]
    estimate_amount = data["estimate_amount"]
    losses_amount = data["losses_amount"]
    paid_amount = data["paid_amount"]

    difference_amount = estimate_amount - repair_fact - losses_amount
    debt_amount = estimate_amount - paid_amount

    if debt_amount < 0:
        debt_amount = 0

    accident_id = await create_accident(
        shift_id=data["shift_id"],
        accident_date=data["accident_date"],
        accident_place=data["accident_place"],
        accident_type=data["accident_type"],
        guilty_party=data["guilty_party"],
        repair_fact=repair_fact,
        estimate_amount=estimate_amount,
        payment_type=data["payment_type"],
        paid_amount=paid_amount,
        downtime_shifts=data["downtime_shifts"],
        losses_amount=losses_amount,
        photo_1=data["photo_1"],
        photo_2=data["photo_2"],
        note=note,
    )

    if not accident_id:
        await message.answer(
            "Не удалось создать ДТП.",
            reply_markup=accident_menu_keyboard()
        )
        await state.clear()
        return

    await message.answer(
        f"✅ ДТП #{accident_id} добавлено.\n\n"
        f"Дата ДТП: {data['accident_date']}\n"
        f"Место: {data['accident_place']}\n"
        f"Тип ДТП: {data['accident_type']}\n"
        f"Виновен: {data['guilty_party']}\n\n"
        f"Факт ремонт: {repair_fact:.0f} сом\n"
        f"Оценка: {estimate_amount:.0f} сом\n"
        f"Оплачено: {paid_amount:.0f} сом\n"
        f"Остаток долга: {debt_amount:.0f} сом\n"
        f"Простой: {data['downtime_shifts']} смен\n"
        f"Потери: {losses_amount:.0f} сом\n"
        f"Разница: {difference_amount:.0f} сом\n\n"
        f"Машина переведена в статус repair.",
        reply_markup=accident_menu_keyboard()
    )

    await state.clear()