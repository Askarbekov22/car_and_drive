from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.drivers import drivers_menu_keyboard
from services.access_service import can_edit_data
from services.driver_service import get_driver_by_id, update_driver_field

router = Router()


class EditDriverState(StatesGroup):
    driver_id = State()
    new_value = State()


def edit_driver_fields_keyboard(driver_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ФИО", callback_data=f"edit_driver_full_name_{driver_id}")],
            [InlineKeyboardButton(text="Телефон", callback_data=f"edit_driver_phone_{driver_id}")],
            [InlineKeyboardButton(text="Адрес", callback_data=f"edit_driver_address_{driver_id}")],
            [InlineKeyboardButton(text="Доп. контакт 1", callback_data=f"edit_driver_extra_contact_1_{driver_id}")],
            [InlineKeyboardButton(text="Доп. контакт 2", callback_data=f"edit_driver_extra_contact_2_{driver_id}")],
            [InlineKeyboardButton(text="Дата принятия", callback_data=f"edit_driver_hire_date_{driver_id}")],
            [InlineKeyboardButton(text="Депозит", callback_data=f"edit_driver_deposit_amount_{driver_id}")],
            [InlineKeyboardButton(text="Долг", callback_data=f"edit_driver_debt_{driver_id}")],
            [InlineKeyboardButton(text="Ущерб", callback_data=f"edit_driver_damage_amount_{driver_id}")],
        ]
    )


@router.message(lambda message: message.text == "✏️ Редактировать водителя")
async def start_edit_driver(message: Message, state: FSMContext):
    if not can_edit_data(message.from_user.id):
        await message.answer("⛔ Редактировать водителей могут только Ырыс и Сыймык.")
        return

    await state.clear()
    await message.answer("Введите ID водителя:")
    await state.set_state(EditDriverState.driver_id)


@router.message(EditDriverState.driver_id)
async def get_driver_id(message: Message, state: FSMContext):
    try:
        driver_id = int(message.text)
    except ValueError:
        await message.answer("Введите ID цифрами.")
        return

    driver = await get_driver_by_id(driver_id)

    if not driver:
        await message.answer("Водитель не найден.")
        return

    await state.clear()

    await message.answer(
        f"Водитель найден:\n\n"
        f"ID: {driver[0]}\n"
        f"ФИО: {driver[1]}\n"
        f"Телефон: {driver[2]}\n"
        f"Адрес: {driver[5]}\n"
        f"Депозит: {driver[10]} сом\n"
        f"Долг: {driver[22]} сом\n\n"
        f"Что изменить?",
        reply_markup=edit_driver_fields_keyboard(driver_id)
    )


@router.callback_query(F.data.startswith("edit_driver_"))
async def choose_driver_field(callback: CallbackQuery, state: FSMContext):
    if not can_edit_data(callback.from_user.id):
        await callback.message.answer("⛔ Редактировать водителей могут только Ырыс и Сыймык.")
        await callback.answer()
        return

    parts = callback.data.split("_")
    driver_id = int(parts[-1])
    field_name = "_".join(parts[2:-1])

    allowed_fields = {
        "full_name": "Введите новое ФИО:",
        "phone": "Введите новый телефон:",
        "address": "Введите новый адрес:",
        "extra_contact_1": "Введите доп. контакт 1:",
        "extra_contact_2": "Введите доп. контакт 2:",
        "hire_date": "Введите дату принятия:",
        "deposit_amount": "Введите сумму депозита:",
        "debt": "Введите сумму долга:",
        "damage_amount": "Введите сумму ущерба:",
    }

    if field_name not in allowed_fields:
        await callback.answer()
        return

    await state.update_data(
        driver_id=driver_id,
        field_name=field_name
    )

    await callback.message.answer(allowed_fields[field_name])
    await state.set_state(EditDriverState.new_value)
    await callback.answer()


@router.message(EditDriverState.new_value)
async def save_driver_new_value(message: Message, state: FSMContext):
    if not can_edit_data(message.from_user.id):
        await message.answer("⛔ Редактировать водителей могут только Ырыс и Сыймык.")
        await state.clear()
        return

    data = await state.get_data()

    driver_id = data["driver_id"]
    field_name = data["field_name"]
    value = message.text.strip()

    if not value:
        await message.answer("Значение не может быть пустым.")
        return

    if field_name in ["deposit_amount", "debt", "damage_amount"]:
        try:
            value = float(value.replace(",", "."))
        except ValueError:
            await message.answer("Введите сумму цифрами.")
            return

    result = await update_driver_field(
        driver_id=driver_id,
        field_name=field_name,
        value=value
    )

    if not result:
        await message.answer("Не удалось обновить водителя.")
        await state.clear()
        return

    await message.answer(
        "✅ Водитель обновлен",
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()