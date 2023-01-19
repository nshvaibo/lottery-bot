"""Daily lottery class"""
import random
from datetime import datetime, timedelta, timezone
from threading import Thread
from time import sleep
import sys # TODO: remove

from telebot.types import MessageEntity

from bot._bot_init import bot
from common import utils
from config import LOTTERY_TIME
from special_users import admin_balance, daily_lottery_fund
from tickets import Tickets
from user import User


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
            if now <= draw_time:
                print(f"{abs(delta).seconds/3600:.2f} hours before the lottery")
            else:
                print(f"{abs(delta).seconds/3600:.2f} hours after the lottery")

            if abs(delta) < timedelta(seconds=1):
                # Conduct draw
                print("draw")
                self._draw()
            elif abs(delta) < timedelta(minutes=1):
                sleep(0.1)
            else:
                sleep(60)
            
            # TODO: remove, used for debugging
            sys.stdout.flush()
            sys.stderr.flush()
    
    def _draw(self, winning_ticket=None):
        # Fetch all purchased tickets
        all_tickets = self.tickets.get_all()

        # Get all users that participate in this draw
        # (all users who purchased tickets)
        participants = set(all_tickets.values())

        # Notify all participants about the draw
        utils.bulk_send_message(bot, "Проводим лотерею!", participants)

        # Generate winning ticket
        if winning_ticket is None:
            winning_ticket = random.randint(100000, 999999)

        # Determine winners
        all_winners = self._determine_winners(winning_ticket, all_tickets)

        # Reveal the winning ticket to participants
        utils.bulk_send_message(bot, f"Выигрышный билет: {winning_ticket}\nС победителями свяжемся отдельно.", participants)

        # Get prize fund for this day
        jackpot = daily_lottery_fund.get_balance()

        # Admin commission
        admin_balance.add_balance(jackpot * 0.02)

        # Notify winners
        sent = set()
        for percentage, winners in all_winners.items():
            msg = f"Выигрышные билеты:"
            for winner in winners:
                if winner["user_id"] not in sent:
                    bot.send_message(winner["user_id"], msg)
                    sent.add(winner["user_id"])
            for winner in winners:
                bot.send_message(winner["user_id"], winner["ticket_num"] + f" - {percentage}% от джекпота")
                
                # Deduct winning amount from user balance
                daily_lottery_fund.withdraw_balance(percentage / 100 * jackpot)
                
                # Send prize to user
                user = User(winner["user_id"])
                user.add_balance(percentage / 100 * jackpot * 0.9)

        # Delete all tickets for this day
        for participant in participants:
            user = User(participant)
            user.remove_tickets()      


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
                    winners[percentages[len(substr)]].append({
                        "user_id": user_id,
                        "ticket_num": ticket_num
                    })
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
