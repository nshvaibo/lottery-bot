from bot import bot, register_handlers
from lottery import DailyLottery
from bot._handlers.general import set_up_manual_draw # TODO: remove manual lottery activation

# TODO: remove try-except
try:
    # Start lottery
    lottery = DailyLottery()
    lottery.start()

    # TODO: remove
    set_up_manual_draw(lottery)

    # Start the bot
    register_handlers()
    bot.infinity_polling()

    # Wait until lottery is done
    lottery.join()
except Exception as err:
    print("Bot main died :(")
    print(err)
    import sys
    sys.stdout.flush()
    sys.stderr.flush()
