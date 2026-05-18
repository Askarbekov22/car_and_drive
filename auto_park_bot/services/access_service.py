from config import (
    YRYS_IDS,
    SYMYK_IDS,
    MANAGER_IDS
)


ROLE_YRYS = "yrys"
ROLE_SYMYK = "symyk"
ROLE_MANAGER = "manager"
ROLE_UNKNOWN = "unknown"


def get_user_role(user_id: int):

    if user_id in YRYS_IDS:
        return ROLE_YRYS

    if user_id in SYMYK_IDS:
        return ROLE_SYMYK

    if user_id in MANAGER_IDS:
        return ROLE_MANAGER

    return ROLE_UNKNOWN


def can_open_section(user_id: int, section: str):

    role = get_user_role(user_id)

    if role in [ROLE_YRYS, ROLE_SYMYK]:
        return True

    if role == ROLE_MANAGER:
        return section in [
            "cars",
            "drivers"
        ]

    return False


def get_role_name(user_id: int):

    role = get_user_role(user_id)

    if role == ROLE_YRYS:
        return "Ырыс"

    if role == ROLE_SYMYK:
        return "Сыймык"

    if role == ROLE_MANAGER:
        return "Менеджер"

    return "Нет доступа"