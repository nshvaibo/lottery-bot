"""Menu interface that can be used for back to menu buttons by all modules"""
from telebot.callback_data import CallbackData
from bot._message_templates import message_templates
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

menu_factory = CallbackData("section", prefix="menu")
def menu_interface(lang: str):
    tickets_button = message_templates[lang]["menu"]["tickets_button"]
    wallet_button = message_templates[lang]["menu"]["wallet_button"]
    keyboard=[[
        InlineKeyboardButton(
            text=tickets_button,
            callback_data=menu_factory.new(section="tickets")
        ),
        InlineKeyboardButton(
            text=wallet_button,
            callback_data=menu_factory.new(section="wallet")
        )
    ]]
    return InlineKeyboardMarkup(keyboard=keyboard, row_width=2)

def back_to_menu(bot, message, lang: str):
    chat_id = message.chat.id
    user_id = message.chat.id
    message_id = message.id

    # Go back to main menu
    main_menu_msg = message_templates[lang]["menu"]["menu_message"]
    bot.edit_message_text(main_menu_msg, chat_id, message_id, reply_markup=menu_interface(lang))
