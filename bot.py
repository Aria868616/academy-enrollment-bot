import logging

import telebot

import config
from database.db import create_db_and_tables
from loader import bot
# Order matters: admin handlers must register before user_handlers, whose
# last handler is a catch-all fallback.
import handlers.admin_handlers  # noqa: F401
import handlers.user_handlers  # noqa: F401  (registers the handlers)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
telebot.logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    create_db_and_tables()
    if not config.ADMIN_IDS:
        logger.warning("ADMIN_IDS is empty: the admin panel is disabled.")
    bot.remove_webhook()
    logger.info("Bot is running and waiting for messages...")
    bot.infinity_polling(skip_pending=True)