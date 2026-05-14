from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.cars import cars_menu_keyboard
from keyboards.main import main_menu_keyboard
from services.car_service import add_car, get_all_cars

router = Router()


class AddCar(StatesGroup):
    plate_number = State()
    model = State()


@router.message(lambda message: message.text == "🚗 Машины")
async def cars_menu(message: Message):
    await message.answer(
        "Раздел машин 🚗",
        reply_markup=cars_menu_keyboard()
    )


@router.message(lambda message: message.text == "➕ Добавить машину")
async def start_add_car(message: Message, state: FSMContext):
    await message.answer("Введите госномер машины:")
    await state.set_state(AddCar.plate_number)


@router.message(AddCar.plate_number)
async def get_plate_number(message: Message, state: FSMContext):
    await state.update_data(plate_number=message.text.upper())
    await message.answer("Введите модель машины:")
    await state.set_state(AddCar.model)


@router.message(AddCar.model)
async def get_model(message: Message, state: FSMContext):
    data = await state.get_data()

    try:
        await add_car(
            plate_number=data["plate_number"],
            model=message.text
        )
        await message.answer(
            "✅ Машина добавлена",
            reply_markup=cars_menu_keyboard()
        )
    except Exception:
        await message.answer(
            "❌ Такая машина уже есть в базе",
            reply_markup=cars_menu_keyboard()
        )

    await state.clear()


@router.message(lambda message: message.text == "📋 Список машин")
async def list_cars(message: Message):
    cars = await get_all_cars()

    if not cars:
        await message.answer("Список машин пуст")
        return

    text = "📋 Список машин:\n\n"

    for car in cars:
        text += (
            f"{car[0]}. {car[1]}\n"
            f"Модель: {car[2]}\n"
            f"Статус: {car[3]}\n\n"
        )

    await message.answer(text)