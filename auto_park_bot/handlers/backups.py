import os

from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.backup import backup_menu_keyboard
from keyboards.main import main_menu_keyboard

from services.access_service import can_edit_data
from services.backup_service import (
    create_database_backup,
    restore_database_from_file,
    RESTORE_DIR
)


router = Router()


class RestoreDatabaseState(StatesGroup):
    waiting_file = State()


@router.message(lambda message: message.text == "🛡 База данных")
async def backup_menu(message: Message):
    if not can_edit_data(message.from_user.id):
        await message.answer("⛔ Доступ только для Ырыса и Сыймыка.")
        return

    await message.answer(
        "Раздел базы данных:",
        reply_markup=backup_menu_keyboard()
    )


@router.message(lambda message: message.text == "📦 Скачать базу")
async def download_database_backup(message: Message):
    if not can_edit_data(message.from_user.id):
        await message.answer("⛔ Скачать базу могут только Ырыс и Сыймык.")
        return

    await message.answer("⏳ Создаю резервную копию базы...")

    archive_path, error = create_database_backup()

    if error:
        await message.answer(f"❌ {error}")
        return

    await message.answer_document(
        FSInputFile(archive_path),
        caption=(
            "📦 Резервная копия базы данных\n\n"
            "Сохрани этот файл в Telegram / Google Drive / компьютер."
        )
    )


@router.message(lambda message: message.text == "♻️ Восстановить базу")
async def start_restore_database(message: Message, state: FSMContext):
    if not can_edit_data(message.from_user.id):
        await message.answer("⛔ Восстанавливать базу могут только Ырыс и Сыймык.")
        return

    await state.clear()

    await message.answer(
        "Отправьте файл базы:\n\n"
        "Поддерживается:\n"
        ".db\n"
        ".sqlite\n"
        ".tar.gz\n\n"
        "⚠️ Текущая база будет заменена."
    )

    await state.set_state(RestoreDatabaseState.waiting_file)


@router.message(RestoreDatabaseState.waiting_file)
async def process_restore_database(message: Message, state: FSMContext):
    if not can_edit_data(message.from_user.id):
        await message.answer("⛔ Доступ запрещён.")
        await state.clear()
        return

    if not message.document:
        await message.answer("Нужно отправить файл базы.")
        return

    os.makedirs(RESTORE_DIR, exist_ok=True)

    filename = message.document.file_name or "uploaded_database.db"

    file_path = os.path.join(
        RESTORE_DIR,
        filename
    )

    await message.bot.download(
        message.document,
        destination=file_path
    )

    await message.answer("⏳ Проверяю и восстанавливаю базу...")

    success, result_text = await restore_database_from_file(file_path)

    if not success:
        await message.answer(f"❌ {result_text}")
        return

    await message.answer(
        result_text,
        reply_markup=backup_menu_keyboard()
    )

    await state.clear()


@router.message(lambda message: message.text == "⬅️ Главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard(message.from_user.id)
    )