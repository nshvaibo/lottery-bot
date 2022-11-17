"""State oblivious handlers (e.g. help messages, default handlers, etc.)"""
from bot._bot_init import bot
from bot._message_templates import message_templates
from bot._handlers.menu_interface import menu_interface

# Manual lottery activation
lottery = None
def set_up_manual_draw(global_lottery):
    """Pass a pointer to lottery to the bot"""
    global lottery 
    lottery = global_lottery

@bot.message_handler(func= lambda msg: msg.text == "lottery")
def force_draw(message):
    lottery._draw()

# Default message handler: any message not expected by the bot
@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'])
def command_default(message):
    lang = message.from_user.language_code

    unknown_msg = message_templates[lang]["general_messages"]["unknown_message"]
    bot.reply_to(message, unknown_msg, reply_markup=menu_interface(lang))
