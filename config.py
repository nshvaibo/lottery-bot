from security_keys.api_key import API_TOKEN
from datetime import time,timezone

GOOGLE_APPLICATION_CREDENTIALS = "/home/nshvaibo/lottery_bot/security_keys/lottery-bot-366521-47477b6ca775.json"
TICKET_PRICE_TON = 1 # Price of the ticket in TON

# UTC time of the daily lottery
LOTTERY_TIME = time(hour=22, minute=1, tzinfo=timezone.utc)
