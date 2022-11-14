from bot import bot, register_handlers
from lottery import Lottery

# Start lottery
lottery = Lottery()
lottery.start()

# Start the bot
register_handlers()
bot.infinity_polling()

# Wait until lottery is done
lottery.join()
