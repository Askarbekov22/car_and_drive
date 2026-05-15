from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.drivers import drivers_menu_keyboard
from keyboards.main import main_menu_keyboard

from services.driver_service import add_driver

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


async def back_to_main(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard(message.from_user.id)
    )


@router.message(lambda message: message.text == "➕ Добавить водителя")
async def start_add_driver(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Введите ФИО водителя:")
    await state.set_state(AddDriver.full_name)


@router.message(AddDriver.full_name)
async def get_full_name(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
        return

    await state.update_data(full_name=message.text)

    await message.answer("Отправьте фото ПАСПОРТА: передняя сторона")
    await state.set_state(AddDriver.passport_front)


@router.message(AddDriver.passport_front)
async def get_passport_front(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
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
        await back_to_main(message, state)
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
        await back_to_main(message, state)
        return

    await state.update_data(address=message.text)

    await message.answer("Введите номер телефона:")
    await state.set_state(AddDriver.phone)


@router.message(AddDriver.phone)
async def get_phone(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
        return

    await state.update_data(phone=message.text)

    await message.answer("Введите доп. контакт №1:")
    await state.set_state(AddDriver.extra_contact_1)


@router.message(AddDriver.extra_contact_1)
async def get_extra_contact_1(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
        return

    await state.update_data(extra_contact_1=message.text)

    await message.answer("Введите доп. контакт №2:")
    await state.set_state(AddDriver.extra_contact_2)


@router.message(AddDriver.extra_contact_2)
async def get_extra_contact_2(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
        return

    await state.update_data(extra_contact_2=message.text)

    await message.answer("Введите дату принятия на работу:")
    await state.set_state(AddDriver.hire_date)


@router.message(AddDriver.hire_date)
async def get_hire_date(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
        return

    await state.update_data(hire_date=message.text)

    await message.answer("Отправьте договор файлом:")
    await state.set_state(AddDriver.contract_file)


@router.message(AddDriver.contract_file)
async def get_contract_file(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await back_to_main(message, state)
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
        await back_to_main(message, state)
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
        await back_to_main(message, state)
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