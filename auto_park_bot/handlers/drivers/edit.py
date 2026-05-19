from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.drivers import drivers_menu_keyboard
from services.access_service import can_edit_data
from services.driver_service import get_driver_by_id, update_driver_field

router = Router()


class EditDriverState(StatesGroup):
    driver_id = State()
    new_value = State()


EDIT_DRIVER_FIELDS = {
    "full_name": "ФИО",
    "phone": "Телефон",
    "passport_front": "Паспорт перед",
    "passport_back": "Паспорт зад",
    "address": "Адрес",
    "extra_contact_1": "Доп. контакт 1",
    "extra_contact_2": "Доп. контакт 2",
    "hire_date": "Дата принятия",
    "contract_file": "Договор",
    "deposit_amount": "Депозит",
    "deposit_receipt": "Чек депозита",
    "deposit_limit": "Лимит депозита",
    "deposit_status": "Статус депозита",
    "total_orders": "Заказы",
    "income_from_driver": "Доход с водителя",
    "total_turnover": "Оборот",
    "damage_amount": "Ущерб",
    "driver_salary_total": "Зарплата",
    "debt": "Долг",
    "fine_amount_total": "Штрафы",
}


NUMERIC_FIELDS = {
    "deposit_amount",
    "deposit_limit",
    "total_orders",
    "income_from_driver",
    "total_turnover",
    "damage_amount",
    "driver_salary_total",
    "debt",
    "fine_amount_total",
}


FILE_FIELDS = {
    "passport_front",
    "passport_back",
    "contract_file",
    "deposit_receipt",
}


def edit_driver_fields_keyboard(driver_id: int):
    keyboard = []

    for field, title in EDIT_DRIVER_FIELDS.items():
        keyboard.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"edit_driver_field:{driver_id}:{field}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


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
        f"Лимит депозита: {driver[12]} сом\n"
        f"Статус депозита: {driver[13]}\n"
        f"Заказы: {driver[14]}\n"
        f"Доход: {driver[15]} сом\n"
        f"Оборот: {driver[16]} сом\n"
        f"Ущерб: {driver[17]} сом\n"
        f"Зарплата: {driver[18]} сом\n"
        f"Долг: {driver[19]} сом\n"
        f"Штрафы: {driver[20]} сом\n\n"
        f"Что изменить?",
        reply_markup=edit_driver_fields_keyboard(driver_id)
    )


@router.callback_query(F.data.startswith("edit_driver_field:"))
async def choose_driver_field(callback: CallbackQuery, state: FSMContext):
    if not can_edit_data(callback.from_user.id):
        await callback.message.answer("⛔ Редактировать водителей могут только Ырыс и Сыймык.")
        await callback.answer()
        return

    _, driver_id, field_name = callback.data.split(":")

    if field_name not in EDIT_DRIVER_FIELDS:
        await callback.answer()
        return

    await state.update_data(
        driver_id=int(driver_id),
        field_name=field_name
    )

    if field_name in FILE_FIELDS:
        await callback.message.answer(
            f"Отправьте новый файл/фото для поля: {EDIT_DRIVER_FIELDS[field_name]}"
        )
    else:
        await callback.message.answer(
            f"Введите новое значение для поля: {EDIT_DRIVER_FIELDS[field_name]}"
        )

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

    if field_name in FILE_FIELDS:
        if message.photo:
            value = message.photo[-1].file_id
        elif message.document:
            value = message.document.file_id
        else:
            await message.answer("Нужно отправить фото или файл.")
            return
    else:
        value = message.text.strip()

        if not value:
            await message.answer("Значение не может быть пустым.")
            return

        if field_name in NUMERIC_FIELDS:
            try:
                if field_name == "total_orders":
                    value = int(value)
                else:
                    value = float(value.replace(",", "."))
            except ValueError:
                await message.answer("Введите число.")
                return

        if field_name == "deposit_status":
            if value not in ["active", "stopped"]:
                await message.answer("Статус депозита должен быть: active или stopped.")
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
        "✅ Данные водителя обновлены",
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()