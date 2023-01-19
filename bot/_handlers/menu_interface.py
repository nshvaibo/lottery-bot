"""Menu interface that can be used for back to menu buttons by all modules"""
import telebot
from telebot.callback_data import CallbackData
from bot._message_templates import message_templates
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from special_users import daily_lottery_fund

menu_factory = CallbackData("section", prefix="menu")
def menu_interface(lang: str):
    markup = InlineKeyboardMarkup()

    tickets_button = message_templates[lang]["menu"]["tickets_button"]
    wallet_button = message_templates[lang]["menu"]["wallet_button"]
    
    tickets_button = InlineKeyboardButton(
        text=tickets_button,
        callback_data=menu_factory.new(section="tickets")
    )

    wallet_button = InlineKeyboardButton(
        text=wallet_button,
        callback_data=menu_factory.new(section="wallet")
    )

    rules_btn_text = message_templates[lang]["menu"]["rules_button"]
    rules_button = InlineKeyboardButton(
        text=rules_btn_text,
        callback_data=menu_factory.new(section="rules")
    )

    referrals_btn_text = message_templates[lang]["menu"]["referrals_button"]
    referrals_button = InlineKeyboardButton(
        text=referrals_btn_text,
        callback_data=menu_factory.new(section="referrals")
    )

    markup.add(wallet_button, row_width=1)
    markup.add(rules_button, tickets_button, row_width=2)
    markup.add(referrals_button, row_width=1)

    return markup

def back_to_main_menu_interface(lang: str):
    markup = telebot.types.InlineKeyboardMarkup()
    
    tomenu_button = message_templates[lang]["menu"]["back_to_menu_button"]
    tomenu_button = telebot.types.InlineKeyboardButton(
        text=tomenu_button,
        callback_data=menu_factory.new(section="back_to_menu")
    )
    markup.add(tomenu_button, row_width=1)
    
    return markup

def back_to_menu(bot, message, lang: str):
    chat_id = message.chat.id
    user_id = message.chat.id
    message_id = message.id

    # Go back to main menu
    jackpot = daily_lottery_fund.get_balance()
    main_menu_msg = message_templates[lang]["menu"]["menu_message"].format(jackpot=jackpot, jackpot_usd=666666)
    bot.edit_message_text(main_menu_msg, chat_id, message_id, reply_markup=menu_interface(lang))
