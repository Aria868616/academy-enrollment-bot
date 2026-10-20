# bot.py
import logging
import telebot
from loader import bot
from database.db import create_db_and_tables
import handlers.user_handlers  # فقط برای ثبت شدن هندلرها

telebot.logger.setLevel(logging.DEBUG)  # موقت، برای دیدن خطاها

if __name__ == "__main__":
    create_db_and_tables()
    print("🤖 Bot is running and waiting for messages...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)