"""Special account to store specific balances."""
from config import BOT_ID
from user import User

# Store administration funds on its balance
admin_balance = User(BOT_ID)

# Daily lottery prize fund
daily_lottery_fund = User("daily_prize")
