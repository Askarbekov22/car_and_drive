import os
import shutil
import sqlite3
import tarfile
from datetime import datetime

from database import DB_NAME, init_db


BACKUP_DIR = "backups"
RESTORE_DIR = "restore_tmp"


def ensure_dirs():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(RESTORE_DIR, exist_ok=True)


def get_timestamp():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def check_database_file(db_path: str):
    if not os.path.exists(db_path):
        return False, "Файл базы не найден."

    if os.path.getsize(db_path) == 0:
        return False, "Файл базы пустой."

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()

        if not integrity_result or integrity_result[0] != "ok":
            connection.close()
            return False, "База повреждена."

        required_tables = [
            "drivers",
            "cars",
            "shifts",
            "accidents",
            "driver_fines"
        ]

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """)

        existing_tables = [
            row[0]
            for row in cursor.fetchall()
        ]

        connection.close()

        for table in required_tables:
            if table not in existing_tables:
                return False, f"В базе нет таблицы: {table}"

        return True, "База корректная."

    except Exception as error:
        return False, f"Ошибка проверки базы: {error}"


def create_database_backup():
    ensure_dirs()

    if not os.path.exists(DB_NAME):
        return None, "Файл базы данных не найден."

    timestamp = get_timestamp()

    db_copy_path = os.path.join(
        BACKUP_DIR,
        f"auto_park_backup_{timestamp}.db"
    )

    archive_path = os.path.join(
        BACKUP_DIR,
        f"auto_park_backup_{timestamp}.tar.gz"
    )

    shutil.copy2(DB_NAME, db_copy_path)

    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(
            db_copy_path,
            arcname="auto_park.db"
        )

    return archive_path, None


def create_backup_before_restore():
    ensure_dirs()

    if not os.path.exists(DB_NAME):
        return None

    timestamp = get_timestamp()

    backup_path = os.path.join(
        BACKUP_DIR,
        f"before_restore_{timestamp}.db"
    )

    shutil.copy2(DB_NAME, backup_path)

    return backup_path


def extract_database_from_archive(archive_path: str):
    ensure_dirs()

    timestamp = get_timestamp()

    extract_path = os.path.join(
        RESTORE_DIR,
        f"restore_{timestamp}"
    )

    os.makedirs(extract_path, exist_ok=True)

    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            archive.extractall(extract_path)

        possible_files = []

        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.endswith(".db") or file.endswith(".sqlite"):
                    possible_files.append(
                        os.path.join(root, file)
                    )

        if not possible_files:
            return None, "В архиве не найден файл базы .db."

        return possible_files[0], None

    except Exception as error:
        return None, f"Не удалось распаковать архив: {error}"


async def restore_database_from_file(uploaded_file_path: str):
    ensure_dirs()

    filename = os.path.basename(uploaded_file_path).lower()

    if filename.endswith(".tar.gz") or filename.endswith(".tgz"):
        db_file_path, error = extract_database_from_archive(uploaded_file_path)

        if error:
            return False, error

    elif filename.endswith(".db") or filename.endswith(".sqlite"):
        db_file_path = uploaded_file_path

    else:
        return False, "Нужен файл .db или .tar.gz"

    is_valid, message = check_database_file(db_file_path)

    if not is_valid:
        return False, message

    backup_before_restore = create_backup_before_restore()

    shutil.copy2(db_file_path, DB_NAME)

    await init_db()

    result_text = "✅ База восстановлена."

    if backup_before_restore:
        result_text += (
            f"\n\nСтарая база сохранена здесь:\n"
            f"{backup_before_restore}"
        )

    return True, result_text