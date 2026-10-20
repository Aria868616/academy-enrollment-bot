# loader.py
from telebot import TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.states.sync.middleware import StateMiddleware
import config


class IsAdminFilter(custom_filters.SimpleCustomFilter):
    """Use as is_admin=True on message and callback-query handlers."""

    key = "is_admin"

    @staticmethod
    def check(obj) -> bool:
        return obj.from_user is not None and obj.from_user.id in config.ADMIN_IDS


state_storage = StateMemoryStorage()
bot = TeleBot(config.BOT_TOKEN, state_storage=state_storage, use_class_middlewares=True)

bot.setup_middleware(StateMiddleware(bot))
bot.add_custom_filter(custom_filters.StateFilter(bot))   # ← اضافه شد
bot.add_custom_filter(IsAdminFilter())