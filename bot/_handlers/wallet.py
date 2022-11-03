import telebot
from bot._bot_init import bot
from bot._message_templates import message_templates
from telebot.callback_data import CallbackData
from telebot.handler_backends import State, StatesGroup
from user import User


# States group.
class States(StatesGroup):
    # Just name variables differently
    adding_balance = State()
    withdrawing_balance = State()

balance_factory = CallbackData("operation", prefix="balance")
def balance_interface(lang: str):
    deposit_button = message_templates[lang]["account_operations"]["deposit_button"]
    withdraw_button = message_templates[lang]["account_operations"]["withdraw_button"]
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

@bot.callback_query_handler(func=balance_factory.filter().check)
def balance_change_callback(call: telebot.types.CallbackQuery):
    callback_data: dict = balance_factory.parse(callback_data=call.data)
    lang = call.from_user.language_code
    if callback_data["operation"] == "add":
        new_text = message_templates[lang]["account_operations"]["deposit_prompt"]
        bot.set_state(call.message.chat.id, States.adding_balance, call.message.chat.id)
    else:
        new_text = message_templates[lang]["account_operations"]["withdraw_prompt"]
        bot.set_state(call.message.chat.id, States.withdrawing_balance, call.message.chat.id)
    
    placeholder_msg = message_templates[lang]["account_operations"]["enter_amount_prompt"]
    bot.send_message(
        chat_id=call.message.chat.id,
        text=new_text,
        reply_markup=telebot.types.ForceReply(input_field_placeholder=placeholder_msg)
    )

# Balance operations handlers
@bot.message_handler(state=States.adding_balance)
def adding_balance(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = message.from_user.language_code

    # Check that the message actually only contains amount
    try:
        amount = float(message.text)
    except ValueError as err:
        bad_format_msg = message_templates[lang]["account_operations"]["incorrect_format"]
        bot.send_message(chat_id, bad_format_msg)
        return
    
    # Retrieve user data from database
    user = User(user_id)

    # Update database and local state with new balance
    user.add_balance(amount)

    # Change state back to normal
    bot.delete_state(user_id, chat_id)

    current_balance_msg = message_templates[lang]["account_operations"]["balance_status"].format(balance = user.get_balance())
    bot.send_message(chat_id, current_balance_msg, reply_markup=balance_interface(lang))

@bot.message_handler(state=States.withdrawing_balance)
def withdrawing_balance(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = message.from_user.language_code

    # Check that the message actually only contains amount
    try:
        amount = float(message.text)
    except ValueError as err:
        bad_format_msg = message_templates[lang]["account_operations"]["incorrect_format"]
        bot.send_message(chat_id, bad_format_msg)
        return
    
    # Retrieve user data from database
    user = User(user_id)

    # Update database and local state with new balance
    if not user.withdraw_balance(amount):
        overdraft_msg = message_templates[lang]["account_operations"]["overdraft_attempt"]
        bot.send_message(chat_id, overdraft_msg)
        return

    # Change state back to normal
    bot.delete_state(user_id, chat_id)

    current_balance_msg = message_templates[lang]["account_operations"]["balance_status"].format(balance = user.get_balance())
    bot.send_message(chat_id, current_balance_msg, reply_markup=balance_interface(lang))
