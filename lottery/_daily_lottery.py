"""Daily lottery class"""
import random
from datetime import datetime, timedelta, timezone
from threading import Thread
from time import sleep

from bot._bot_init import bot
from special_users import admin_balance, daily_lottery_fund
from config import LOTTERY_TIME
from tickets import Tickets


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
    
    def _draw(self, winning_ticket=None):
        bot.send_message(176854476, "Проводим лотерею!")

        # Generate winning ticket
        if winning_ticket is None:
            winning_ticket = random.randint(100000, 999999)

        # Fetch all purchased tickets
        all_tickets = self.tickets.get_all()

        # Determine winners
        winners = self._determine_winners(winning_ticket, all_tickets)

        print(winners)
    
    def _determine_winners(self, winning_ticket, all_tickets):
        """
        Returns winners (user_ids) in the following format:
        {
            x1% of prize fund: [user1, user2, ...]),
            x2% of prize fund: [user1, user2, ...]),
            ...
        }

        For example:
        (3%, [user1, user2])
        """
        # Maps matching combination lengths to % of prize fund
        # (length: %)
        percentages = {
            2: 3,
            3: 5,
            4: 15,
            5: 25,
            6: 50
        }

        winners = {
            3: [],
            5: [],
            15: [],
            25: [],
            50: []
        }

        # Generate all possible winning combinations
        substrings = get_substrings(str(winning_ticket))
        
        for ticket_num, user_id in all_tickets.items():
            for substr in substrings:
                # Ignore matches with one digit
                if len(substr) == 1:
                    continue

                if str(ticket_num).find(substr) != -1:
                    winners[percentages[len(substr)]].append(user_id)
                    break
        
        return winners 


# Helper functions

def get_substrings(x):
    """Generate all unique substrings of the given string"""
    allSubStrings = set()

    # Go through all possible lengths of substrings
    for i in range(0, len(x)):
        # Generate substrings of given length
        for k in range(0, len(x) - i):
            #append substring to resulting set
            allSubStrings.add(x[k:i+k+1])

    allSubStringsList = list(allSubStrings)
    allSubStringsList.sort(key=len, reverse=True)

    return allSubStringsList
