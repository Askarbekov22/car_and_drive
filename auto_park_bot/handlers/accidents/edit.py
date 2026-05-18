from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.accident_keyboards import (
    accident_menu_keyboard,
    edit_accident_fields_keyboard,
    edit_payment_type_keyboard
)

from services.accident_service import (
    get_accident_by_id,
    update_accident_field,
    close_accident
)

router = Router()


class EditAccidentState(StatesGroup):
    accident_id = State()
    new_value = State()


@router.message(lambda message: message.text == "✏️ Редактировать ДТП")
async def edit_accident_start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ID ДТП, которое нужно редактировать:")
    await state.set_state(EditAccidentState.accident_id)


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
    accident_id = int(data.split("_")[-1])

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

    await callback.message.answer(text)
    await state.set_state(EditAccidentState.new_value)

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
            await message.answer("Неверный формат. Например: 2026-05-14")
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