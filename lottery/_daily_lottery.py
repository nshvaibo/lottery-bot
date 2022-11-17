"""Daily lottery class"""
from datetime import datetime, timedelta, timezone
from threading import Thread
from time import sleep

from bot._bot_init import bot
from tickets import Tickets
from config import LOTTERY_TIME


class DailyLottery(Thread):
    def __init__(self) -> None:
        Thread.__init__(self)
        
        self.tickets = Tickets("daily")

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

        tickets = []
        for i in range(10000):
            tickets.append(i)

        tickets = self.tickets.get_all()
        print("a")
        # import time
        # start = time.time()
        # self.tickets.add_tickets(tickets, "user")
        # end = time.time()

        # print(f"took {end - start} seconds")
