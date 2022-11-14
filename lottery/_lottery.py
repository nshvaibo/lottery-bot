from datetime import datetime, timedelta, timezone
from threading import Thread
from time import sleep

from bot._bot_init import bot
from config import LOTTERY_TIME


class Lottery(Thread):
    def __init__(self) -> None:
        Thread.__init__(self)

    def run(self):
        while True:
            # Check if it's time for the draw
            today = datetime.now(timezone.utc).date()
            draw_time = datetime.combine(today, LOTTERY_TIME, tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = now - draw_time
            if abs(delta) < timedelta(seconds=1):
                # Conduct draw
                self._draw()
            elif abs(delta) < timedelta(minutes=1):
                sleep(0.1)
            else:
                sleep(60)
    
    def _draw(self):
        bot.send_message(176854476, "draw")
        sleep(60)
