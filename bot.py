import logging

import telebot

from database.db import create_db_and_tables
from loader import bot
import handlers.user_handlers  # noqa: F401  (registers the handlers)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
telebot.logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    create_db_and_tables()
    bot.remove_webhook()
    logger.info("Bot is running and waiting for messages...")
    bot.infinity_polling(skip_pending=True)