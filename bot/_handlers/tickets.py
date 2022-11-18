import random

import telebot
from telebot.callback_data import CallbackData
from telebot.handler_backends import State, StatesGroup

from bot._bot_init import bot
from bot._handlers.menu_interface import back_to_menu
from bot._message_templates import message_templates
from config import TICKET_PRICE_TON
from tickets import Tickets
from user import User
from special_users import daily_lottery_fund, admin_balance


# States group.
class WalletStates(StatesGroup):
    # Just name variables differently
    buying_tickets = State() # In this state user selects the number of tickets they want to buy
    confirming_purchase = State() # Confirm requested purchase

tickets_factory = CallbackData("operation", "number", prefix="tickets")
def tickets_interface(lang: str):
    my_tickets_button = message_templates[lang]["tickets"]["my_tickets_button"]
    buy_button = message_templates[lang]["tickets"]["buy_tickets_button"]
    tomenu_button_msg = message_templates[lang]["menu"]["back_to_menu_button"]

    keyboard=[[
        telebot.types.InlineKeyboardButton(
            text=my_tickets_button,
            callback_data=tickets_factory.new(operation="status", number="-1")
        ),
        telebot.types.InlineKeyboardButton(
            text=buy_button,
            callback_data=tickets_factory.new(operation="buy", number="-1")
        )
    ]]
    
    # Add tickets buttons to interface
    markup = telebot.types.InlineKeyboardMarkup(keyboard=keyboard, row_width=2)

    # Add back to main menu button
    tomenu_button = telebot.types.InlineKeyboardButton(
        text=tomenu_button_msg,
        callback_data=tickets_factory.new(operation="back_to_menu", number="-1")
    )
    markup.add(tomenu_button, row_width=1)
    
    return markup

def cart_interface(lang: str):
    back_button_msg = message_templates[lang]["tickets"]["back_button"]

    keyboard=[[
        telebot.types.InlineKeyboardButton(
            text="1",
            callback_data=tickets_factory.new(number="1", operation="")
        ),
        telebot.types.InlineKeyboardButton(
            text="2",
            callback_data=tickets_factory.new(number="2", operation="")
        ),
        telebot.types.InlineKeyboardButton(
            text="3",
            callback_data=tickets_factory.new(number="3", operation="")
        )
    ]]
    
    # Add tickets buttons to interface
    markup = telebot.types.InlineKeyboardMarkup(keyboard=keyboard, row_width=2)

    # Add back to tickets menu button
    back_button = telebot.types.InlineKeyboardButton(
        text=back_button_msg,
        callback_data=tickets_factory.new(operation="back_to_tickets", number="-1")
    )
    markup.add(back_button, row_width=1)
    
    return markup

def confirmation_interface(lang: str, num_tickets):
    confirm_button = message_templates[lang]["tickets"]["confirm_button"]
    discard_button = message_templates[lang]["tickets"]["discard_button"]

    keyboard=[[
        telebot.types.InlineKeyboardButton(
            text=confirm_button,
            callback_data=tickets_factory.new(operation="confirm", number=str(num_tickets))
        ),
        telebot.types.InlineKeyboardButton(
            text=discard_button,
            callback_data=tickets_factory.new(operation="back_to_tickets", number="-1")
        )
    ]]
    
    # Add tickets buttons to interface
    markup = telebot.types.InlineKeyboardMarkup(keyboard=keyboard, row_width=2)
    
    return markup

def back_button_interface(lang: str):
    back_button_msg = message_templates[lang]["tickets"]["back_button"]
    
    # Create markup object
    markup = telebot.types.InlineKeyboardMarkup()

    # Add back to tickets menu button
    back_button = telebot.types.InlineKeyboardButton(
        text=back_button_msg,
        callback_data=tickets_factory.new(operation="back_to_tickets", number="-1")
    )
    markup.add(back_button, row_width=1)
    
    return markup


# Tickets operation handlers

@bot.callback_query_handler(func=tickets_factory.filter(number="-1").check)
def buy_tickets_callback(call: telebot.types.CallbackQuery):
    callback_data: dict = tickets_factory.parse(callback_data=call.data)
    chat_id = call.message.chat.id
    user_id = call.message.chat.id
    message_id = call.message.id
    lang = call.from_user.language_code
    
    enter_amount_msg = message_templates[lang]["wallet"]["enter_amount_prompt"]
    if callback_data["operation"] == "buy":
        # Retrieve user data from database
        user = User(user_id)
    
        buy_prompt = message_templates[lang]["tickets"]["how_many_tickets_prompt"]
        buy_prompt = buy_prompt.format(ton_price=TICKET_PRICE_TON, balance=user.get_balance())

        # Wait till user gets back to us with the number of tickets they want to buy
        bot.set_state(call.message.chat.id, WalletStates.buying_tickets, call.message.chat.id)

        # Change interface to selecting the number of tickets
        bot.edit_message_text(buy_prompt, chat_id, message_id, reply_markup=cart_interface(lang))
    elif callback_data["operation"] == "status":
        # Retrieve user data from database
        user = User(user_id)
        tickets = user.get_tickets() # Ticket numbers that belong to this user

        # If no tickets
        if len(tickets) == 0:
            status_msg = message_templates[lang]["tickets"]["status_no_tickets_message"]
        else:
            status_msg = message_templates[lang]["tickets"]["status_message"]
            tickets_str = "".join([f"\t🌟{ticket}\n" for ticket in tickets])
            status_msg = status_msg.format(num_tickets=len(tickets), tickets=tickets_str)
        
        # Report status to the user
        bot.edit_message_text(status_msg, chat_id, message_id, reply_markup=back_button_interface(lang))
    elif callback_data["operation"] == "back_to_menu":
        # Discard all current operations in progress
        bot.delete_state(user_id, chat_id)
        
        # Go back to main menu
        back_to_menu(bot, call.message, lang)
    elif callback_data["operation"] == "back_to_tickets":
        # Discard all current operations in progress
        bot.delete_state(user_id, chat_id)
        
        tickets_menu_msg = message_templates[lang]["tickets"]["tickets_menu_message"]
        # Go back to home page of tickets menu
        bot.edit_message_text(tickets_menu_msg, chat_id, message_id, reply_markup=tickets_interface(lang))
    else:
        raise RuntimeError("Unknown tickets menu option")    
        

@bot.message_handler(state=WalletStates.buying_tickets)
def buying_tickets(message, lang=None, num_tickets=None):
    chat_id = message.chat.id
    user_id = message.chat.id
    if lang is None:
        lang = message.from_user.language_code

    if num_tickets is None:
        num_tickets = message.text

    # Check that the message actually only contains amount
    try:
        num_tickets = int(num_tickets)
    except ValueError as err:
        bad_format_msg = message_templates[lang]["general_messages"]["invalid_number_message"]
        bot.send_message(chat_id, bad_format_msg)
        return
    
    # Retrieve user data from database
    user = User(user_id)

    # Make sure that the user has enough funds to purchase the desired num of tickets
    if num_tickets * TICKET_PRICE_TON > user.get_balance():
        insufficient_funds_msg = message_templates[lang]["tickets"]["insufficient_funds_message"]
        bot.send_message(chat_id, insufficient_funds_msg, reply_markup=back_button_interface(lang))
        return
    
    if num_tickets > 200:
        bot.delete_state(chat_id)
        bot.send_message(chat_id, "Многовато билетов, пока не можем столько продать за раз...")
        return
    
    # Proceed to confirmation of purchase step
    bot.set_state(chat_id, WalletStates.confirming_purchase, chat_id)

    # Save number of tickets user wants to buy
    # Should only confirm the same number as requested
    bot.add_data(chat_id, chat_id, num_tickets=num_tickets)
    
    # Ask the user to confirm purchase
    confirmation_msg = message_templates[lang]["tickets"]["confirmation_request_message"]
    confirmation_msg = confirmation_msg.format(num_tickets=num_tickets)
    bot.send_message(chat_id, confirmation_msg, reply_markup=confirmation_interface(lang, num_tickets))
    

@bot.callback_query_handler(func=tickets_factory.filter(operation="confirm").check, state=WalletStates.confirming_purchase)
def confirm_purchase(call: telebot.types.CallbackQuery):
    """Confirm the purchase of the selected number of tickets"""
    callback_data: dict = tickets_factory.parse(callback_data=call.data)
    chat_id = call.message.chat.id
    user_id = call.message.chat.id
    lang = call.from_user.language_code
    num_tickets = int(callback_data["number"])


    with bot.retrieve_data(chat_id, chat_id) as data:
        # Make sure we are confirming the requested purchase
        if num_tickets != data["num_tickets"]:
            # Delete all state, back to normal operation
            bot.delete_state(chat_id, chat_id)
            
            wrong_conf_msg = message_templates[lang]["tickets"]["wrong_confirmation_message"]
            bot.send_message(chat_id, wrong_conf_msg, reply_markup=back_button_interface(lang))



    # Retrieve user data from the database
    user = User(user_id)

    # Make sure that the user has enough funds to purchase the desired num of tickets
    if num_tickets * TICKET_PRICE_TON > user.get_balance():
        insufficient_funds_msg = message_templates[lang]["tickets"]["insufficient_funds_at_confirmation_message"]
        bot.send_message(chat_id, insufficient_funds_msg, reply_markup=back_button_interface(lang))
        return

    # Update database and local state with new balance
    tickets = [] # List of purchased tickets
    for _ in range(num_tickets):
        # Generate random number
        # TODO: use better algorithm
        ticket = random.randint(100000, 999999)
        tickets.append(ticket)

        # Add ticket to user profile in the database
        success = user.purchase_ticket(ticket)
        if not success:
            insufficient_funds_msg = message_templates[lang]["tickets"]["partially_insufficient_funds_message"]
            insufficient_funds_msg = insufficient_funds_msg.format(num_tickets=len(tickets))
            bot.send_message(chat_id, insufficient_funds_msg, reply_markup=back_button_interface(lang))
        else:
            # 90% of the ticket price goes to prize fund
            daily_lottery_fund.add_balance(0.9)

            # 10% of the ticket price goes to administration
            admin_balance.add_balance(0.1)
    
    # Add all purchased tickets to the draw for this lottery
    tickets_db = Tickets("daily")
    tickets_db.add_tickets(tickets, user_id)


    # Format ticket message in the following way:
    # "Purchased ticket numbers:"
    # "     - ticket_num1"
    # "     - ticket_num2"
    # "     - ..........."
    success_msg = message_templates[lang]["tickets"]["successful_purchase_message"]
    tickets = "".join([f"\t🌟{ticket}\n" for ticket in tickets])
    success_msg = success_msg.format(tickets=tickets, balance=user.get_balance())

    # Announce ticket numbers to users
    bot.send_message(chat_id, success_msg, reply_markup=back_button_interface(lang))

    # Delete all state, back to normal operation
    bot.delete_state(user_id, chat_id)

@bot.callback_query_handler(func=tickets_factory.filter(operation="").check)
def buy_tickets_num_callback(call: telebot.types.CallbackQuery):
    """Receives the number of tickets from callback buttons"""
    callback_data: dict = tickets_factory.parse(callback_data=call.data)
    num_tickets = int(callback_data["number"])
    lang = call.from_user.language_code

    buying_tickets(call.message, lang, num_tickets)
