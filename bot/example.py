"""Examples of different bot use cases"""
import config
import telebot
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import StateFilter
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from user import User

message_templates = config.message_templates

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
    deposit_button = message_templates["account_operations"]["deposit_button"]
    withdraw_button = message_templates["account_operations"]["withdraw_button"]
    keyboard=[[
        telebot.types.InlineKeyboardButton(
            text=deposit_button,
            callback_data=balance_factory.new(operation="add")
        ),
        telebot.types.InlineKeyboardButton(
            text=withdraw_button,
            callback_data=balance_factory.new(operation="withdraw")
        )
    ]]
    return telebot.types.InlineKeyboardMarkup(keyboard=keyboard, row_width=2)

@bot.message_handler(commands=["start"])
def command_start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Retrieve user data from database
    user = User(user_id)

    # If user hasn't used the "/start" command yet:
    if user.is_first_time_user():
        welcome_msg = message_templates["general_messages"]["welcome_message"].format(name = message.from_user.first_name)
        bot.send_message(chat_id, welcome_msg)
    else:
        known_user_msg = message_templates["general_messages"]["already_registered"]
        bot.send_message(chat_id, known_user_msg)

    current_balance_msg = message_templates["account_operations"]["balance_status"].format(balance = user.get_balance())
    bot.send_message(chat_id, current_balance_msg, reply_markup=balance_interface())

@bot.callback_query_handler(func=balance_factory.filter().check)
def products_callback(call: telebot.types.CallbackQuery):
    callback_data: dict = balance_factory.parse(callback_data=call.data)
    if callback_data["operation"] == "add":
        new_text = message_templates["account_operations"]["deposit_prompt"]
        bot.set_state(call.message.chat.id, MyStates.adding_balance, call.message.chat.id)
    else:
        new_text = message_templates["account_operations"]["withdraw_prompt"]
        bot.set_state(call.message.chat.id, MyStates.withdrawing_balance, call.message.chat.id)
    
    placeholder_msg = message_templates["account_operations"]["enter_amount_prompt"]
    bot.send_message(
        chat_id=call.message.chat.id,
        text=new_text,
        reply_markup=telebot.types.ForceReply(input_field_placeholder=placeholder_msg)
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
        bad_format_msg = message_templates["account_operations"]["incorrect_format"]
        bot.send_message(chat_id, bad_format_msg)
        return
    
    # Retrieve user data from database
    user = User(user_id)

    # Update database and local state with new balance
    user.add_balance(amount)

    # Change state back to normal
    bot.delete_state(user_id, chat_id)

    current_balance_msg = message_templates["account_operations"]["balance_status"].format(balance = user.get_balance())
    bot.send_message(chat_id, current_balance_msg, reply_markup=balance_interface())

@bot.message_handler(state=MyStates.withdrawing_balance)
def adding_balance(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check that the message actually only contains amount
    try:
        amount = float(message.text)
    except ValueError as err:
        bad_format_msg = message_templates["account_operations"]["incorrect_format"]
        bot.send_message(chat_id, bad_format_msg)
        return
    
    # Retrieve user data from database
    user = User(user_id)

    # Update database and local state with new balance
    if not user.withdraw_balance(amount):
        overdraft_msg = message_templates["account_operations"]["overdraft_attempt"]
        bot.send_message(chat_id, overdraft_msg)
        return

    # Change state back to normal
    bot.delete_state(user_id, chat_id)

    current_balance_msg = message_templates["account_operations"]["balance_status"].format(balance = user.get_balance())
    bot.send_message(chat_id, current_balance_msg, reply_markup=balance_interface())

# Default message handler: any message not expected by the bot
@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
    'text', 'location', 'contact', 'sticker'])
def command_default(message):
    unknown_msg = message_templates["general_messages"]["unknown_message"]
    bot.reply_to(message, unknown_msg)
