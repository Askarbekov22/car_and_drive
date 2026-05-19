from config import (
    YRYS_IDS,
    SYMYK_IDS,
    MANAGER_IDS
)

from constants.roles import (
    ROLE_YRYS,
    ROLE_SYMYK,
    ROLE_MANAGER,
    ROLE_UNKNOWN
)


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

    if role in [
        ROLE_YRYS,
        ROLE_SYMYK
    ]:
        return True

    if role == ROLE_MANAGER:
        return section in [
            "cars",
            "drivers",
            "reports",
            "shifts",
            "accidents"
        ]

    return False


def can_edit_data(user_id: int):
    role = get_user_role(user_id)

    return role in [
        ROLE_YRYS,
        ROLE_SYMYK
    ]


def get_role_name(user_id: int):
    role = get_user_role(user_id)

    if role == ROLE_YRYS:
        return "Ырыс"

    if role == ROLE_SYMYK:
        return "Сыймык"

    if role == ROLE_MANAGER:
        return "Менеджер"

    return "Нет доступа"