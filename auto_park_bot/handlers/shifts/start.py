from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.shifts import (
    drivers_keyboard,
    cars_keyboard,
    shifts_menu_keyboard
)

from services.driver_service import get_all_drivers
from services.car_service import get_all_cars
from services.shift_service import create_shift

router = Router()


class StartShiftState(StatesGroup):
    choosing_driver = State()
    choosing_car = State()
    start_front_photo = State()
    start_back_photo = State()
    start_left_photo = State()
    start_right_photo = State()


@router.message(lambda message: message.text == "▶️ Начать смену")
async def start_shift(message: Message, state: FSMContext):
    await state.clear()

    drivers = await get_all_drivers()

    if not drivers:
        await message.answer("Нет водителей.")
        return

    await message.answer(
        "Выберите водителя:",
        reply_markup=drivers_keyboard(drivers)
    )

    await state.set_state(StartShiftState.choosing_driver)


@router.message(StartShiftState.choosing_driver)
async def choose_driver(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.clear()
        return

    drivers = await get_all_drivers()
    driver_dict = {
        driver[1]: driver[0]
        for driver in drivers
    }

    if message.text not in driver_dict:
        await message.answer("Выберите водителя из списка.")
        return

    await state.update_data(driver_id=driver_dict[message.text])

    cars = await get_all_cars()
    free_cars = [
        car for car in cars
        if car[3] == "free"
    ]

    if not free_cars:
        await message.answer("Нет свободных машин.")
        await state.clear()
        return

    await message.answer(
        "Выберите машину:",
        reply_markup=cars_keyboard(free_cars)
    )

    await state.set_state(StartShiftState.choosing_car)


@router.message(StartShiftState.choosing_car)
async def choose_car(message: Message, state: FSMContext):
    cars = await get_all_cars()
    free_cars = [
        car for car in cars
        if car[3] == "free"
    ]

    car_dict = {
        car[1]: car[0]
        for car in free_cars
    }

    if message.text not in car_dict:
        await message.answer("Выберите машину из списка.")
        return

    await state.update_data(car_id=car_dict[message.text])

    await message.answer("Отправьте фото ПЕРЕДА машины:")
    await state.set_state(StartShiftState.start_front_photo)


@router.message(StartShiftState.start_front_photo)
async def get_start_front_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(start_front_photo=message.photo[-1].file_id)

    await message.answer("Отправьте фото ЗАДА машины:")
    await state.set_state(StartShiftState.start_back_photo)


@router.message(StartShiftState.start_back_photo)
async def get_start_back_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(start_back_photo=message.photo[-1].file_id)

    await message.answer("Отправьте фото ЛЕВОЙ стороны:")
    await state.set_state(StartShiftState.start_left_photo)


@router.message(StartShiftState.start_left_photo)
async def get_start_left_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(start_left_photo=message.photo[-1].file_id)

    await message.answer("Отправьте фото ПРАВОЙ стороны:")
    await state.set_state(StartShiftState.start_right_photo)


@router.message(StartShiftState.start_right_photo)
async def get_start_right_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Нужно отправить фото.")
        return

    await state.update_data(start_right_photo=message.photo[-1].file_id)

    data = await state.get_data()

    await create_shift(
        driver_id=data["driver_id"],
        car_id=data["car_id"],
        start_front_photo=data["start_front_photo"],
        start_back_photo=data["start_back_photo"],
        start_left_photo=data["start_left_photo"],
        start_right_photo=data["start_right_photo"]
    )

    await message.answer(
        "✅ Смена начата",
        reply_markup=shifts_menu_keyboard()
    )

    await state.clear()