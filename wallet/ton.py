import json
import pprint
from datetime import datetime, timedelta, timezone

from requests import Request, Session

from lock_generator import LockGenerator
from security_keys.api_key import COINMARKETCAP_TOKEN

lock_generator = LockGenerator()
# TODO: figure out locks
class TONRate:
    """Provides an updated USD/TON exchange rate on demand"""
    def __init__(self) -> None:
        self._rate = -1 # USD/TON rate
        self._last_update = datetime.min
        self._update_rate()

    def _update_rate(self):
        url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest" # Coinmarketcap API url

        parameters = { "id": 11419, "convert": "USD" } # API parameters to pass in for retrieving specific cryptocurrency data

        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": COINMARKETCAP_TOKEN
        } # Replace 'YOUR_API_KEY' with the API key you have recieved in the previous step

        session = Session()
        session.headers.update(headers)

        response = session.get(url, params=parameters)
        info = json.loads(response.text)

        self._last_update = datetime.now(timezone.utc)
        self._rate = info["data"]["11419"]["quote"]["USD"]["price"]

    def get_rate(self):
        # lock = lock_generator.get_lock("TONRate", read_only=True)
        now = datetime.now(timezone.utc)
        delta = now - self._last_update
        if not abs(delta) < timedelta(seconds=1):
            # lock.release()
            self._update_rate()

        return self._rate

ton_rate = TONRate()
