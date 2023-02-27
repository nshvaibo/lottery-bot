"""Handle /start command"""
from bot._bot_init import bot
from bot._handlers.menu_interface import menu_interface
from bot._message_templates import message_templates
from special_users import daily_lottery_fund
from user import User
from referrals import Referrals


@bot.message_handler(commands=["start"])
def command_start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = message.from_user.language_code
    
    # Retrieve user data from database
    user = User(user_id)

    # If user hasn't used the "/start" command yet:
    if user.is_first_time_user():
        jackpot = daily_lottery_fund.get_balance()
        welcome_msg = message_templates[lang]["general_messages"]["welcome_message"].format(jackpot=jackpot, jackpot_usd=666666)
        args = message.text.split()
        if len(args) == 2:
            ref_code = args[1]
            refs = Referrals()
            exists, referral_id = refs.get_user_id(ref_code)
            if not exists:
                incorrect_ref_msg = message_templates[lang]["referrals"]["incorrect_refcode_message"]
                bot.send_message(chat_id, incorrect_ref_msg, reply_markup=menu_interface(lang))
            else:
                user.add_referral(referral_id)
                
                # Notify the user who invited this user
                joined_msg = message_templates[lang]["referrals"]["invitee_joined_message"]
                bot.send_message(chat_id, joined_msg, reply_markup=menu_interface(lang))

        bot.send_message(chat_id, welcome_msg, reply_markup=menu_interface(lang))
    else:
        known_user_msg = message_templates[lang]["general_messages"]["already_registered"]
        bot.send_message(chat_id, known_user_msg, reply_markup=menu_interface(lang))
