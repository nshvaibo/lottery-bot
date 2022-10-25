"""Initialization of the bot"""
import telebot

import config
from user import User

bot = telebot.TeleBot(config.API_TOKEN, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

@bot.message_handler(commands=["start"])
def command_start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Retrieve user data from database
    user = User(user_id)

    # If user hasn't used the "/start" command yet:
    if user.is_first_time_user():
        bot.send_message(chat_id, f"Добро пожаловать, {message.from_user.first_name}")
    else:
        bot.send_message(chat_id, "Мы уже знакомы, рад вновь тебя видеть!")

# Default message handler: any message not expected by the bot
@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document',
    'text', 'location', 'contact', 'sticker'])
def command_default(message):
    bot.reply_to(message, f"Извините, я не понял, что вы хотели сказать\nПопробуйте посмотреть список команд /help")
