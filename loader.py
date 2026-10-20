# loader.py
from telebot import TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.states.sync.middleware import StateMiddleware
import config

state_storage = StateMemoryStorage()
bot = TeleBot(config.BOT_TOKEN, state_storage=state_storage, use_class_middlewares=True)

bot.setup_middleware(StateMiddleware(bot))
bot.add_custom_filter(custom_filters.StateFilter(bot))   # ← اضافه شد
