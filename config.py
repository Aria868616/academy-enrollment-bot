import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# استخراج توکن و آدرس دیتابیس
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = os.getenv("DB_NAME", "sqlite:///academy.db")

# بررسی صحت وجود توکن ضروری
if not BOT_TOKEN:
    raise ValueError("خطا: توکن ربات در فایل .env یافت نشد! 🔑")