from security_keys.api_key import API_TOKEN
from security_keys.admin import BOT_ID
from datetime import time,timezone

GOOGLE_APPLICATION_CREDENTIALS = "/home/nshvaibo/lottery_bot/security_keys/lottery-bot-366521-47477b6ca775.json"
TICKET_PRICE_TON = 1 # Price of the ticket in TON

# UTC time of the daily lottery
# Right now set to 12:00 Moscow time (noon)
LOTTERY_TIME = time(hour=9, minute=0, tzinfo=timezone.utc)

# Base for referrals link generation
# REF_LINK_BASE = "http://t.me/mAUoyMqbCvPYGbTx_bot"    # Lottery bot
REF_LINK_BASE = "http://t.me/n3GL24rd8eKE_bot"          # Development bot
