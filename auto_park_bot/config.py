import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

admin_id = os.getenv("ADMIN_ID")
if admin_id is None:
    raise ValueError("❌ ADMIN_ID не найден в .env")

ADMIN_ID = int(admin_id)