import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "❌ BOT_TOKEN не найден в .env"
    )


def parse_ids(value: str | None):

    if not value:
        return []

    result = []

    for item in value.split(","):

        item = item.strip()

        if item:
            result.append(int(item))

    return result


ADMIN_ID = int(
    os.getenv("ADMIN_ID", "0")
)

YRYS_IDS = parse_ids(
    os.getenv("YRYS_IDS")
)

SYMYK_IDS = parse_ids(
    os.getenv("SYMYK_IDS")
)

MANAGER_IDS = parse_ids(
    os.getenv("MANAGER_IDS")
)

if ADMIN_ID and ADMIN_ID not in YRYS_IDS:
    YRYS_IDS.append(ADMIN_ID)