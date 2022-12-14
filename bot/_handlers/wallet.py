import telebot
from bot._bot_init import bot
from bot._message_templates import message_templates
from bot._handlers.menu_interface import back_to_menu
from telebot.callback_data import CallbackData
from telebot.handler_backends import State, StatesGroup
from user import User
from special_users import admin_balance


# States group.
class States(StatesGroup):
    # Just name variables differently
    adding_balance = State()
    withdrawing_balance = State()

balance_factory = CallbackData("operation", prefix="balance")
def wallet_interface(lang: str):
    deposit_button = message_templates[lang]["wallet"]["deposit_button"]
    withdraw_button = message_templates[lang]["wallet"]["withdraw_button"]
    tomenu_button = message_templates[lang]["menu"]["back_to_menu_button"]
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
    
    markup = telebot.types.InlineKeyboardMarkup(keyboard=keyboard, row_width=2)
    tomenu_button = telebot.types.InlineKeyboardButton(
        text=tomenu_button,
        callback_data=balance_factory.new(operation="back_to_menu")
    )
    markup.add(tomenu_button, row_width=1)
    
    return markup

def back_button_interface(lang: str):
    back_button_msg = message_templates[lang]["wallet"]["back_button"]
    
    # Create markup object
    markup = telebot.types.InlineKeyboardMarkup()

    # Add back to tickets menu button
    back_button = telebot.types.InlineKeyboardButton(
        text=back_button_msg,
        callback_data=balance_factory.new(operation="back_to_wallet")
    )
    markup.add(back_button, row_width=1)
    
    return markup

def operation_interface(lang: str):
    min_button_msg = message_templates[lang]["wallet"]["min_button"]
    max_button_msg = message_templates[lang]["wallet"]["max_button"]
    back_button_msg = message_templates[lang]["wallet"]["back_button"]
    
    # Create markup object
    markup = telebot.types.InlineKeyboardMarkup()

    # Add back to tickets menu button
    min_button = telebot.types.InlineKeyboardButton(
        text=min_button_msg,
        callback_data=balance_factory.new(operation="min")
    )
    
    # Add back to tickets menu button
    max_button = telebot.types.InlineKeyboardButton(
        text=max_button_msg,
        callback_data=balance_factory.new(operation="max")
    )
    markup.add(min_button, max_button, row_width=2)
    
    # Add back to tickets menu button
    back_button = telebot.types.InlineKeyboardButton(
        text=back_button_msg,
        callback_data=balance_factory.new(operation="back_to_wallet")
    )
    markup.add(back_button, row_width=1)
    
    return markup

@bot.callback_query_handler(func=balance_factory.filter().check, state=States.adding_balance)
def minmax_deposit_callback(call: telebot.types.CallbackQuery):
    """Input min/max for deposit operation"""
    callback_data: dict = balance_factory.parse(callback_data=call.data)
    chat_id = call.message.chat.id
    user_id = call.message.from_user.id
    lang = call.message.from_user.language_code
    class Placeholder:
        pass
    class Message:
        def __init__(self) -> None:
            self.chat = Placeholder()
            self.from_user = Placeholder()
            self.text = "-1"
    message = Message()
    setattr(message.chat, "id", chat_id)
    setattr(message.from_user, "id", chat_id)
    setattr(message.from_user, "language_code", lang)
    if callback_data["operation"] == "min":
        adding_balance(message, min=True)
    elif callback_data["operation"] == "max":
        max_msg = message_templates[call.from_user.language_code]["wallet"]["max_deposit_message"]
        bot.send_message(call.message.chat.id, max_msg)

@bot.callback_query_handler(func=balance_factory.filter().check, state=States.withdrawing_balance)
def minmax_withdrawing_callback(call: telebot.types.CallbackQuery):
    """Input min/max for deposit operation"""
    callback_data: dict = balance_factory.parse(callback_data=call.data)
    chat_id = call.message.chat.id
    user_id = call.message.from_user.id
    lang = call.message.from_user.language_code
    class Placeholder:
        pass
    class Message:
        def __init__(self) -> None:
            self.chat = Placeholder()
            self.from_user = Placeholder()
            self.text = "-1"
    message = Message()
    setattr(message.chat, "id", chat_id)
    setattr(message.from_user, "id", chat_id)
    setattr(message.from_user, "language_code", lang)

    if callback_data["operation"] == "min":
        withdrawing_balance(message, min=True)
    elif callback_data["operation"] == "max":
        withdrawing_balance(message, max=True)

@bot.callback_query_handler(func=balance_factory.filter().check)
def balance_change_callback(call: telebot.types.CallbackQuery):
    callback_data: dict = balance_factory.parse(callback_data=call.data)
    chat_id = call.message.chat.id
    user_id = call.message.chat.id
    message_id = call.message.id
    lang = call.from_user.language_code
    
    enter_amount_msg = message_templates[lang]["wallet"]["enter_amount_prompt"]
    if callback_data["operation"] == "add":
        new_text = message_templates[lang]["wallet"]["deposit_prompt"]
        bot.set_state(call.message.chat.id, States.adding_balance, call.message.chat.id)
        bot.edit_message_text(new_text, chat_id, message_id, reply_markup=operation_interface(lang))
    elif callback_data["operation"] == "withdraw":
        new_text = message_templates[lang]["wallet"]["withdraw_prompt"]
        bot.set_state(call.message.chat.id, States.withdrawing_balance, call.message.chat.id)
        bot.edit_message_text(new_text, chat_id, message_id, reply_markup=operation_interface(lang))
    elif callback_data["operation"] == "back_to_wallet":
        # Get user data from database
        user = User(chat_id)

        # Discard all current operations in progress
        bot.delete_state(user_id, chat_id)
        
        # Go back to wallet menu
        balance_msg = message_templates[lang]["wallet"]["balance_status"]
        balance_msg = balance_msg.format(balance=user.get_balance())
        bot.edit_message_text(balance_msg, chat_id, message_id, reply_markup=wallet_interface(lang))
    elif callback_data["operation"] == "back_to_menu":
        # Discard all current operations in progress
        bot.delete_state(user_id, chat_id)
        
        # Go back to main menu
        back_to_menu(bot, call.message, lang)


# Balance operations handlers
@bot.message_handler(state=States.adding_balance)
def adding_balance(message, min=False, max=False):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = message.from_user.language_code

    # Check that the message actually only contains amount
    try:
        amount = float(message.text)
    except ValueError as err:
        bad_format_msg = message_templates[lang]["general_messages"]["invalid_number_message"]
        bot.send_message(chat_id, bad_format_msg)
        return
    
    # Retrieve user data from database
    user = User(user_id)

    if min:
        amount = 1

    # Update database and local state with new balance
    user.add_balance(amount)

    # Change state back to normal
    bot.delete_state(user_id, chat_id)

    current_balance_msg = message_templates[lang]["wallet"]["balance_status"].format(balance = user.get_balance())
    bot.send_message(chat_id, current_balance_msg, reply_markup=wallet_interface(lang))

@bot.message_handler(state=States.withdrawing_balance)
def withdrawing_balance(message, min=False, max=False):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = message.from_user.language_code

    # Check that the message actually only contains amount
    try:
        amount = float(message.text)
    except ValueError as err:
        bad_format_msg = message_templates[lang]["wallet"]["incorrect_format"]
        bot.send_message(chat_id, bad_format_msg)
        return
    
    # Retrieve user data from database
    user = User(user_id)

    if min:
        amount = 1
    if max:
        amount = user.get_balance()

    # Update database and local state with new balance
    if not user.withdraw_balance(amount):
        overdraft_msg = message_templates[lang]["wallet"]["overdraft_attempt"]
        bot.send_message(chat_id, overdraft_msg)
        return
    else:
        # Add 10% to admin balance
        admin_balance.add_balance(amount * 0.1)

    # Change state back to normal
    bot.delete_state(user_id, chat_id)

    current_balance_msg = message_templates[lang]["wallet"]["balance_status"].format(balance = user.get_balance())
    bot.send_message(chat_id, current_balance_msg, reply_markup=wallet_interface(lang))
