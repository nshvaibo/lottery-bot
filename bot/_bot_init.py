"""Initialization of the bot"""
import config
import telebot
from telebot.custom_filters import StateFilter
from telebot.storage import StateMemoryStorage

# Initialize state storage for current state of the bot for the current user
state_storage = StateMemoryStorage()

# Telegram bot API
bot = telebot.TeleBot(
    config.API_TOKEN,
    parse_mode=None,
    num_threads=4,
    state_storage=state_storage
)

# Filter messages depending on the internal state for current client
bot.add_custom_filter(StateFilter(bot))
