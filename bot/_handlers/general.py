"""State oblivious handlers (e.g. help messages, default handlers, etc.)"""
from bot._bot_init import bot
from bot._message_templates import message_templates
from bot._handlers.menu import menu_interface

# Default message handler: any message not expected by the bot
@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'text', 'location', 'contact', 'sticker'])
def command_default(message):
    lang = message.from_user.language_code

    unknown_msg = message_templates[lang]["general_messages"]["unknown_message"]
    bot.reply_to(message, unknown_msg, reply_markup=menu_interface(lang))
