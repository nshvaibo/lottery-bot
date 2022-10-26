"""Initialization of the bot"""
from requests import delete
import telebot
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import StateFilter
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

import config
from user import User

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(
    config.API_TOKEN,
    parse_mode=None,
    num_threads=4,
    state_storage=state_storage
)

bot.add_custom_filter(StateFilter(bot))

# States group.
class MyStates(StatesGroup):
    # Just name variables differently
    adding_balance = State()
    withdrawing_balance = State()

balance_factory = CallbackData("operation", prefix="balance")
def balance_interface():
    keyboard=[[
        telebot.types.InlineKeyboardButton(
            text="Пополнить",
            callback_data=balance_factory.new(operation="add")
        ),
        telebot.types.InlineKeyboardButton(
            text="Снять",
            callback_data=balance_factory.new(operation="withdraw")
        )

    ],[telebot.types.InlineKeyboardButton(
            text="Fake",
            callback_data="other_callback"
        )]]
    return telebot.types.InlineKeyboardMarkup(keyboard=keyboard, row_width=2)

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
        bot.send_message(chat_id, "Мы уже знакомы, рад вновь вас видеть!")

    bot.send_message(chat_id, f"Баланс: {user.get_balance()} TON", reply_markup=balance_interface())

@bot.callback_query_handler(func=balance_factory.filter().check)
def products_callback(call: telebot.types.CallbackQuery):
    callback_data: dict = balance_factory.parse(callback_data=call.data)
    if callback_data["operation"] == "add":
        new_text = f"Напишите сумму, на которую вы хотите пополнить кошелек."
        bot.set_state(call.message.chat.id, MyStates.adding_balance, call.message.chat.id)
    else:
        new_text = f"Напишите, какую сумму вы хотите вывести."
        bot.set_state(call.message.chat.id, MyStates.withdrawing_balance, call.message.chat.id)
    
    bot.send_message(
        chat_id=call.message.chat.id,
        text=new_text,
        reply_markup=telebot.types.ForceReply(input_field_placeholder="Введите сумму: ")
    )

# Balance operations handlers
@bot.message_handler(state=MyStates.adding_balance)
def adding_balance(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check that the message actually only contains amount
    try:
        amount = float(message.text)
    except ValueError as err:
        bot.send_message(chat_id, f"Пожалуйста пришлите сумму в верном формате")
        return
    
    # Retrieve user data from database
    user = User(user_id)

    # Update database and local state with new balance
    user.add_balance(amount)

    # Change state back to normal
    bot.delete_state(user_id, chat_id)

    bot.send_message(chat_id, f"Новый баланс: {user.get_balance()} TON", reply_markup=balance_interface())

@bot.message_handler(state=MyStates.withdrawing_balance)
def adding_balance(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check that the message actually only contains amount
    try:
        amount = float(message.text)
    except ValueError as err:
        bot.send_message(chat_id, f"Пожалуйста пришлите сумму в верном формате")
        return
    
    # Retrieve user data from database
    user = User(user_id)

    # Update database and local state with new balance
    if not user.withdraw_balance(amount):
        bot.send_message(chat_id, f"Хитро! Попробуйте еще раз)")
        return

    # Change state back to normal
    bot.delete_state(user_id, chat_id)

    bot.send_message(chat_id, f"Новый баланс: {user.get_balance()} TON", reply_markup=balance_interface())

# Default message handler: any message not expected by the bot
@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
    'text', 'location', 'contact', 'sticker'])
def command_default(message):
    bot.reply_to(message, f"Извините, я не понял, что вы хотели сказать\nПопробуйте посмотреть список команд /help")
