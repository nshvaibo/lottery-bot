import logging
import time
from pathlib import Path

from bot import bot, register_handlers
from bot._handlers.general import \
    set_up_manual_draw  # TODO: remove manual lottery activation
from common.utils import find_last_log
from config import LOG_LEVEL, LOGS_FOLDER, LOGGER_NAME
from lottery import DailyLottery

# Set up logging for lottery bot
log_number = find_last_log() + 1
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOG_LEVEL)
# Define the file handler
path = Path(LOGS_FOLDER) / f"log{log_number}.txt"
file_handler = logging.FileHandler(path)
# Define the log format
formatter = logging.Formatter("%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
formatter.converter = time.gmtime
file_handler.setFormatter(formatter)
# Add the file handler to the logger
logger.addHandler(file_handler)
logger.info("Lottery bot logger started")

# Set up logging for TeleBot
logger = logging.getLogger("TeleBot")
logger.setLevel(logging.DEBUG)
# Disable the console handler
logger.handlers[0].setLevel(logging.NOTSET)
logger.removeHandler(logger.handlers[0])
path = Path(LOGS_FOLDER) / f"TeleBot_log{log_number}.txt"
file_handler = logging.FileHandler(path)
formatter = logging.Formatter(
    '###########################################################\n%(asctime)s.%(msecs)03d (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"\n###########################################################\n\n',
    datefmt="%d/%m/%Y %H:%M:%S"
)
formatter.converter = time.gmtime
file_handler.setFormatter(formatter)
file_handler.setLevel(LOG_LEVEL)
# Add the file handler to the logger
logger.addHandler(file_handler)
logger.info("TeleBot logger started")

# TODO: remove try-except
try:
    # Start lottery
    lottery = DailyLottery()
    lottery.start()

    # TODO: remove
    set_up_manual_draw(lottery)

    # Start the bot
    register_handlers()
    bot.infinity_polling(logger_level=logging.NOTSET)

    # Wait until lottery is done
    lottery.join()
except Exception as err:
    logger.critical(f"Exiting main.py with error:\n{err}")
