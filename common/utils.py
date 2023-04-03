"""Helper functions for use in all submodules"""

import random


def bulk_send_message(bot, message=None, users_ids=None, map=None):
    """
    Send <message> to each user in <user_ids> in bulk.
    Alternatively, send different message to each user in the map.
    The map should be formated as (user_id: message)
    """
    
    if message is not None and users_ids is not None:
        for user_id in users_ids:
            bot.send_message(user_id, message)

    elif map is not None:
        for user_id, msg in map.items():
            bot.send_message(user_id, msg)
    
    else:
        raise RuntimeError("Incorrect use of bulk_send_message()")

def generate_random_ticket() -> int:
    """Returns the number of a randomly generated ticket"""
    return random.randint(100000, 999999)