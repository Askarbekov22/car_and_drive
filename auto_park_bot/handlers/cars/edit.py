from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.cars import (
    edit_car_fields_keyboard,
    cars_menu_keyboard
)

from services.car_service import (
    get_car_by_id,
    update_car_field
)

router = Router()


class EditCarState(StatesGroup):
    car_id = State()
    new_value = State()


@router.message(lambda message: message.text == "✏️ Редактировать машину")
async def start_edit_car(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ID машины:")
    await state.set_state(EditCarState.car_id)


@router.message(EditCarState.car_id)
async def get_car_id(message: Message, state: FSMContext):
    try:
        car_id = int(message.text)
    except ValueError:
        await message.answer("Введите ID цифрами.")
        return

    car = await get_car_by_id(car_id)

    if not car:
        await message.answer("Машина не найдена.")
        return

    await state.clear()

    await message.answer(
        f"Машина найдена:\n\n"
        f"Госномер: {car[1]}\n"
        f"Модель: {car[2]}\n"
        f"Статус: {car[3]}\n\n"
        f"Что хотите изменить?",
        reply_markup=edit_car_fields_keyboard(car_id)
    )


@router.callback_query(F.data.startswith("edit_car_"))
async def choose_car_field(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if "plate" in data:
        field_name = "plate_number"
        text = "Введите новый госномер:"

    elif "model" in data:
        field_name = "model"
        text = "Введите новую модель:"

    elif "status" in data:
        field_name = "status"
        text = (
            "Введите новый статус:\n\n"
            "free\n"
            "busy\n"
            "repair"
        )

    else:
        await callback.answer()
        return

    car_id = int(data.split("_")[-1])

    await state.update_data(
        car_id=car_id,
        field_name=field_name
    )

    await callback.message.answer(text)

    await state.set_state(EditCarState.new_value)

    await callback.answer()


@router.message(EditCarState.new_value)
async def save_car_new_value(message: Message, state: FSMContext):
    data = await state.get_data()

    car_id = data["car_id"]
    field_name = data["field_name"]

    value = message.text.strip()

    if not value:
        await message.answer("Значение не может быть пустым.")
        return

    if field_name == "status":
        allowed = ["free", "busy", "repair"]

        if value not in allowed:
            await message.answer(
                "Статус должен быть:\n"
                "free / busy / repair"
            )
            return

    result = await update_car_field(
        car_id=car_id,
        field_name=field_name,
        value=value
    )

    if not result:
        await message.answer("Не удалось обновить машину.")
        await state.clear()
        return

    await message.answer(
        "✅ Машина обновлена",
        reply_markup=cars_menu_keyboard()
    )

    await state.clear()