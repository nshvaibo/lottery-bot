import logging
from datetime import time, timezone

from security_keys.admin import BOT_ID
from security_keys.api_key import API_TOKEN

GOOGLE_APPLICATION_CREDENTIALS = "/home/nshvaibo/lottery_bot/security_keys/lottery-bot-366521-47477b6ca775.json"
TICKET_PRICE_TON = 1 # Price of the ticket in TON

# UTC time of the daily lottery
# Right now set to 12:00 Moscow time (noon)
LOTTERY_TIME = time(hour=9, minute=0, tzinfo=timezone.utc)

# Base for referrals link generation
# REF_LINK_BASE = "http://t.me/mAUoyMqbCvPYGbTx_bot"    # Lottery bot
REF_LINK_BASE = "http://t.me/n3GL24rd8eKE_bot"          # Development bot

# Base for the relative logs path
LOGS_FOLDER = "../logs/"
# Logging level depth
# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = logging.DEBUG
# Logger name for the application
LOGGER_NAME = "lottery_bot_logger"
