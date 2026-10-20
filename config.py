import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# استخراج توکن و آدرس دیتابیس
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = os.getenv("DB_NAME", "sqlite:///academy.db")
def _parse_admin_ids(raw: str) -> set[int]:
    """Parse a comma-separated list of Telegram IDs, ignoring blanks/typos."""
    return {int(part) for part in raw.split(",") if part.strip().isdigit()}


ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))

# بررسی صحت وجود توکن ضروری
if not BOT_TOKEN:
    raise ValueError("خطا: توکن ربات در فایل .env یافت نشد! 🔑")