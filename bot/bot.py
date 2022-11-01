"""Initialization of the bot"""
import json

import config
import telebot
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import StateFilter
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from user import User

# Templated messages for different languages
with open("message_templates/general_template.json") as f:
    message_templates = json.load(f)

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

# Default message handler: any message not expected by the bot
@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'])
def command_default(message):
    unknown_msg = message_templates["general_messages"]["unknown_message"]
    bot.reply_to(message, unknown_msg)
