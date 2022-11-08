"""Main menu handlers"""
import telebot
from bot._bot_init import bot
from bot._handlers.wallet import balance_interface
from bot._handlers.tickets import tickets_interface
from bot._handlers.menu_interface import menu_factory
from bot._message_templates import message_templates
from user import User


@bot.callback_query_handler(func=menu_factory.filter().check)
def menu_callback(call: telebot.types.CallbackQuery):
    callback_data: dict = menu_factory.parse(callback_data=call.data)
    
    chat_id = call.message.chat.id
    message_id = call.message.id
    lang = call.from_user.language_code

    # Get user data from database
    user = User(chat_id)

    if callback_data["section"] == "tickets":
        tickets_msg = message_templates[lang]["tickets"]["tickets_menu_message"]
        bot.edit_message_text(tickets_msg, chat_id, message_id, reply_markup=tickets_interface(lang))
    elif callback_data["section"] == "wallet":
        balance_msg = message_templates[lang]["account_operations"]["balance_status"]
        balance_msg = balance_msg.format(balance=user.get_balance())
        bot.edit_message_text(balance_msg, chat_id, message_id, reply_markup=balance_interface(lang))
    else:
        raise RuntimeError("Unknown menu option")
