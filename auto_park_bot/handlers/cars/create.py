from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.cars import cars_menu_keyboard

from services.car_service import add_car

router = Router()


class AddCarState(StatesGroup):
    plate_number = State()
    model = State()


@router.message(lambda message: message.text == "➕ Добавить машину")
async def start_add_car(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите госномер машины:")
    await state.set_state(AddCarState.plate_number)


@router.message(AddCarState.plate_number)
async def get_plate_number(message: Message, state: FSMContext):
    plate_number = message.text.strip()

    if not plate_number:
        await message.answer("Введите госномер.")
        return

    await state.update_data(plate_number=plate_number)

    await message.answer("Введите модель машины:")
    await state.set_state(AddCarState.model)


@router.message(AddCarState.model)
async def get_model(message: Message, state: FSMContext):
    model = message.text.strip()

    if not model:
        await message.answer("Введите модель.")
        return

    data = await state.get_data()

    await add_car(
        plate_number=data["plate_number"],
        model=model
    )

    await message.answer(
        "✅ Машина добавлена",
        reply_markup=cars_menu_keyboard()
    )

    await state.clear()