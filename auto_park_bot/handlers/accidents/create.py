from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.accident_keyboards import (
    accident_menu_keyboard,
    payment_type_keyboard
)

from services.accident_service import create_accident
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
        await message.answer("Смена не найдена. Проверь ID смены.")
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

    if len(accident_date) != 10 or accident_date[4] != "-" or accident_date[7] != "-":
        await message.answer("Неверный формат. Например: 2026-05-14")
        return

    await state.update_data(accident_date=accident_date)

    await message.answer("Введите сумму ущерба:")
    await state.set_state(AccidentState.damage_amount)


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
        "insurance": "Страховая",
        "mixed": "Смешанная оплата"
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
        paid_amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите оплаченную сумму цифрами.")
        return

    if paid_amount < 0:
        await message.answer("Оплаченная сумма не может быть меньше нуля.")
        return

    await state.update_data(paid_amount=paid_amount)

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
            "Не удалось создать ДТП.",
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
        f"Сумма ущерба: {data['damage_amount']:.0f} сом\n"
        f"Оплачено: {data['paid_amount']:.0f} сом\n"
        f"Остаток: {debt_amount:.0f} сом\n\n"
        f"Машина переведена в статус repair.",
        reply_markup=accident_menu_keyboard()
    )

    await state.clear()