"""State oblivious handlers (e.g. help messages, default handlers, etc.)"""
from bot._bot_init import bot
from bot._message_templates import message_templates
from bot._handlers.menu_interface import menu_interface

# Store pointer to the lottery object
lottery = None
def set_up_manual_draw(global_lottery):
    """Pass a pointer to lottery to the bot"""
    global lottery 
    lottery = global_lottery

# Manually activates lottery
@bot.message_handler(func= lambda msg: msg.text.find("lottery") != -1)
def force_draw(message):
    idx = message.text.find(":")
    if idx != -1:
        lottery._draw(message.text[idx+1:])
    else:
        lottery._draw()

@bot.message_handler(func= lambda msg: msg.text == "status")
def get_admin_status(message):
    from special_users import admin_balance, daily_lottery_fund
    from datetime import datetime, timezone
    
    text = f"Баланс администрации: {admin_balance.get_balance()} TON\n\n"

    today = datetime.now(timezone.utc).date().strftime("%d.%m.%Y")
    text += f"Призовой фонд на {today} составляет: {daily_lottery_fund.get_balance()} TON"
    
    bot.reply_to(message, text)

# Default message handler: any message not expected by the bot
@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'])
def command_default(message):
    lang = message.from_user.language_code

    unknown_msg = message_templates[lang]["general_messages"]["unknown_message"]
    bot.reply_to(message, unknown_msg, reply_markup=menu_interface(lang))
