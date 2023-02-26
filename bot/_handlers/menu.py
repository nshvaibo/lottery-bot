"""Main menu handlers"""
import telebot
from bot._bot_init import bot
from bot._handlers.wallet import wallet_interface, goto_wallet_menu
from bot._handlers.tickets import tickets_interface, goto_tickets_menu
from bot._handlers.menu_interface import back_to_main_menu_interface, menu_interface
from bot._handlers.menu_interface import menu_factory, back_to_menu
from bot._message_templates import message_templates
from user import User


@bot.callback_query_handler(func=menu_factory.filter().check)
def menu_callback(call: telebot.types.CallbackQuery):
    callback_data: dict = menu_factory.parse(callback_data=call.data)
    
    chat_id = call.message.chat.id
    message_id = call.message.id
    lang = call.from_user.language_code

    if callback_data["section"] == "tickets":
        goto_tickets_menu(chat_id, lang, message_id)
    elif callback_data["section"] == "wallet":
        goto_wallet_menu(chat_id, lang, message_id)
    elif callback_data["section"] == "rules":
        rules_msg = message_templates[lang]["rules"]["message"]
        bot.edit_message_text(rules_msg, chat_id, message_id, reply_markup=back_to_main_menu_interface(lang))
    elif callback_data["section"] == "referrals":
        user = User(chat_id)
        ref_link = user.get_ref_link()
        referrals_msg = message_templates[lang]["referrals"]["referrals_menu_message"]
        referrals_msg = referrals_msg.format(ref_link=ref_link)
        bot.edit_message_text(referrals_msg, chat_id, message_id, reply_markup=back_to_main_menu_interface(lang))
    elif callback_data["section"] == "back_to_menu":
        back_to_menu(bot, call.message, lang)
    else:
        raise RuntimeError("Unknown menu option")
