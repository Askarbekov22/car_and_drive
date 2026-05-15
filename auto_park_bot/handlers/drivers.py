from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.drivers import drivers_menu_keyboard
from keyboards.main import main_menu_keyboard

from services.driver_service import (
    add_driver,
    get_all_drivers_full,
    get_driver_shift_history,
    get_driver_income_history,
    get_driver_income_summary,
    get_drivers_rating,
    search_drivers
)

router = Router()


class AddDriver(StatesGroup):
    full_name = State()
    passport_front = State()
    passport_back = State()
    address = State()
    phone = State()
    extra_contact_1 = State()
    extra_contact_2 = State()
    hire_date = State()
    contract_file = State()
    deposit_amount = State()
    deposit_receipt = State()


class DriverHistoryState(StatesGroup):
    shift_history_driver = State()
    income_history_driver = State()


class DriverSearchState(StatesGroup):
    search_query = State()


@router.message(lambda message: message.text == "⬅️ Назад")
async def universal_back(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard()
    )


@router.message(lambda message: message.text == "👤 Водители")
async def drivers_menu(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Раздел водителей 👤",
        reply_markup=drivers_menu_keyboard()
    )


@router.message(lambda message: message.text == "➕ Добавить водителя")
async def start_add_driver(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите ФИО водителя:")
    await state.set_state(AddDriver.full_name)


@router.message(AddDriver.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Отправьте фото ПАСПОРТА: передняя сторона")
    await state.set_state(AddDriver.passport_front)


@router.message(AddDriver.passport_front)
async def get_passport_front(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    if not message.photo:
        await message.answer("Нужно отправить фото паспорта.")
        return

    await state.update_data(passport_front=message.photo[-1].file_id)
    await message.answer("Отправьте фото ПАСПОРТА: задняя сторона")
    await state.set_state(AddDriver.passport_back)


@router.message(AddDriver.passport_back)
async def get_passport_back(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    if not message.photo:
        await message.answer("Нужно отправить фото паспорта.")
        return

    await state.update_data(passport_back=message.photo[-1].file_id)
    await message.answer("Введите место проживания:")
    await state.set_state(AddDriver.address)


@router.message(AddDriver.address)
async def get_address(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    await state.update_data(address=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(AddDriver.phone)


@router.message(AddDriver.phone)
async def get_phone(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    await state.update_data(phone=message.text)
    await message.answer("Введите доп. контакт №1:")
    await state.set_state(AddDriver.extra_contact_1)


@router.message(AddDriver.extra_contact_1)
async def get_extra_contact_1(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    await state.update_data(extra_contact_1=message.text)
    await message.answer("Введите доп. контакт №2:")
    await state.set_state(AddDriver.extra_contact_2)


@router.message(AddDriver.extra_contact_2)
async def get_extra_contact_2(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    await state.update_data(extra_contact_2=message.text)
    await message.answer("Введите дату принятия на работу:")
    await state.set_state(AddDriver.hire_date)


@router.message(AddDriver.hire_date)
async def get_hire_date(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    await state.update_data(hire_date=message.text)
    await message.answer("Отправьте договор файлом:")
    await state.set_state(AddDriver.contract_file)


@router.message(AddDriver.contract_file)
async def get_contract_file(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    if not message.document:
        await message.answer("Нужно отправить договор файлом.")
        return

    await state.update_data(contract_file=message.document.file_id)
    await message.answer("Введите сумму депозита:")
    await state.set_state(AddDriver.deposit_amount)


@router.message(AddDriver.deposit_amount)
async def get_deposit_amount(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    try:
        deposit_amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите сумму числом.")
        return

    await state.update_data(deposit_amount=deposit_amount)
    await message.answer("Отправьте фото чека депозита:")
    await state.set_state(AddDriver.deposit_receipt)


@router.message(AddDriver.deposit_receipt)
async def get_deposit_receipt(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    if not message.photo:
        await message.answer("Нужно отправить фото чека.")
        return

    await state.update_data(deposit_receipt=message.photo[-1].file_id)

    data = await state.get_data()

    await add_driver(
        full_name=data["full_name"],
        phone=data["phone"],
        passport_front=data["passport_front"],
        passport_back=data["passport_back"],
        address=data["address"],
        extra_contact_1=data["extra_contact_1"],
        extra_contact_2=data["extra_contact_2"],
        hire_date=data["hire_date"],
        contract_file=data["contract_file"],
        deposit_amount=data["deposit_amount"],
        deposit_receipt=data["deposit_receipt"]
    )

    await message.answer(
        "✅ Водитель добавлен",
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "📋 Список водителей")
async def list_drivers(message: Message):
    drivers = await get_all_drivers_full()

    if not drivers:
        await message.answer("Список водителей пуст.")
        return

    text = "📋 Список водителей:\n\n"

    for driver in drivers:
        text += (
            f"ФИО: {driver[1]}\n"
            f"Телефон: {driver[2]}\n"
            f"Депозит: {driver[3] or 0:.0f} сом\n"
            f"Статус депозита: {driver[4]}\n"
            f"Заказы: {driver[5] or 0}\n"
            f"Оборот: {driver[7] or 0:.0f} сом\n"
            f"Зарплата: {driver[9] or 0:.0f} сом\n"
            f"Долг: {driver[10] or 0:.0f} сом\n\n"
        )

    await message.answer(text)


@router.message(lambda message: message.text == "🔎 Поиск водителя")
async def start_driver_search(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ФИО или номер телефона:")
    await state.set_state(DriverSearchState.search_query)


@router.message(DriverSearchState.search_query)
async def process_driver_search(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    drivers = await search_drivers(message.text.strip())

    if not drivers:
        await message.answer(
            "Водитель не найден.\n"
            "Введите другое ФИО или номер телефона."
        )
        return

    text = "🔎 Результаты поиска:\n\n"

    for driver in drivers:
        text += (
            f"ФИО: {driver[1]}\n"
            f"Телефон: {driver[2]}\n"
            f"Депозит: {driver[3] or 0:.0f} сом\n"
            f"Статус депозита: {driver[4]}\n"
            f"Заказы: {driver[5] or 0}\n"
            f"Оборот: {driver[7] or 0:.0f} сом\n"
            f"Зарплата: {driver[9] or 0:.0f} сом\n"
            f"Долг: {driver[10] or 0:.0f} сом\n\n"
        )

    await message.answer(
        text,
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "🕘 История смен водителя")
async def start_driver_shift_history(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ФИО или номер телефона:")
    await state.set_state(DriverHistoryState.shift_history_driver)


@router.message(DriverHistoryState.shift_history_driver)
async def show_driver_shift_history(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    drivers = await search_drivers(message.text.strip())

    if not drivers:
        await message.answer(
            "Водитель не найден.\n"
            "Введите другое ФИО или номер телефона."
        )
        return

    driver = drivers[0]
    shifts = await get_driver_shift_history(driver[0])

    if not shifts:
        await message.answer(
            f"У водителя {driver[1]} пока нет смен.",
            reply_markup=drivers_menu_keyboard()
        )
        await state.clear()
        return

    text = (
        f"🕘 История смен водителя\n\n"
        f"Водитель: {driver[1]}\n\n"
    )

    for shift in shifts:
        text += (
            f"Смена #{shift[0]}\n"
            f"Машина: {shift[1]} {shift[2]}\n"
            f"Заказы: {shift[3] or 0}\n"
            f"Оборот: {shift[4] or 0:.0f} сом\n"
            f"Зарплата: {shift[5] or 0:.0f} сом\n"
            f"Зарядка: {shift[6] or 0:.0f} сом\n"
            f"Комиссия Яндекса: {shift[7] or 0:.0f} сом\n"
            f"Заряд машины: {shift[8] or 0}%\n"
            f"Начало: {shift[9]}\n"
            f"Конец: {shift[10]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "💰 История дохода водителя")
async def start_driver_income_history(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ФИО или номер телефона:")
    await state.set_state(DriverHistoryState.income_history_driver)


@router.message(DriverHistoryState.income_history_driver)
async def show_driver_income_history(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await universal_back(message, state)
        return

    drivers = await search_drivers(message.text.strip())

    if not drivers:
        await message.answer(
            "Водитель не найден.\n"
            "Введите другое ФИО или номер телефона."
        )
        return

    driver = drivers[0]

    summary = await get_driver_income_summary(driver[0])
    income_history = await get_driver_income_history(driver[0])

    text = (
        f"💰 История дохода водителя\n\n"
        f"Водитель: {driver[1]}\n\n"
        f"Всего смен: {summary[0] or 0}\n"
        f"Всего заказов: {summary[1] or 0}\n"
        f"Общий оборот: {summary[2] or 0:.0f} сом\n"
        f"Общая зарплата: {summary[3] or 0:.0f} сом\n"
        f"Средний оборот: {summary[4] or 0:.0f} сом\n"
        f"Средняя зарплата: {summary[5] or 0:.0f} сом\n\n"
        f"Последние смены:\n\n"
    )

    for row in income_history:
        text += (
            f"Смена #{row[0]}\n"
            f"Оборот: {row[1] or 0:.0f} сом\n"
            f"Фактическая зарплата: {row[2] or 0:.0f} сом\n"
            f"Процент: {row[3] or 0}%\n"
            f"Рекомендовано: {row[4] or 0:.0f} сом\n"
            f"Дата: {row[5]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=drivers_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "🏆 Рейтинг водителей")
async def show_drivers_rating(message: Message):
    rating = await get_drivers_rating()

    if not rating:
        await message.answer("Рейтинг пуст.")
        return

    text = "🏆 Рейтинг водителей\n\n"

    place = 1

    for row in rating:
        score = (
            (row[3] or 0) * 2
            + (row[4] or 0) / 1000
            - (row[7] or 0) / 1000
            - (row[8] or 0) / 1000
        )

        text += (
            f"{place}. {row[1]}\n"
            f"Смен: {row[2] or 0}\n"
            f"Заказы: {row[3] or 0}\n"
            f"Оборот: {row[4] or 0:.0f} сом\n"
            f"Средний оборот: {row[6] or 0:.0f} сом\n"
            f"Долг: {row[7] or 0:.0f} сом\n"
            f"Ущерб: {row[8] or 0:.0f} сом\n"
            f"Рейтинг: {score:.1f}\n\n"
        )

        place += 1

    await message.answer(text)