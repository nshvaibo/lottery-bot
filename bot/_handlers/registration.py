"""Handle /start command"""
from bot._bot_init import bot
from bot._handlers.wallet import balance_interface
from bot._message_templates import message_templates
from user import User


@bot.message_handler(commands=["start"])
def command_start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = message.from_user.language_code
    
    # Retrieve user data from database
    user = User(user_id)

    # If user hasn't used the "/start" command yet:
    if user.is_first_time_user():
        welcome_msg = message_templates[lang]["general_messages"]["welcome_message"].format(name = message.from_user.first_name)
        bot.send_message(chat_id, welcome_msg)
    else:
        known_user_msg = message_templates[lang]["general_messages"]["already_registered"]
        bot.send_message(chat_id, known_user_msg)

    current_balance_msg = message_templates[lang]["account_operations"]["balance_status"].format(balance = user.get_balance())
    bot.send_message(chat_id, current_balance_msg, reply_markup=balance_interface(lang))
