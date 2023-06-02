"""Helper functions for use in all submodules"""

import random
from pathlib import Path

from config import LOG_LEVEL, LOGS_FOLDER


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

##########################################################
#################### HELPER FUNCTIONS ####################
##########################################################

# Returns number of last log in the logs folder
def find_last_log() -> int:
    log_files = [path.name for path in Path(LOGS_FOLDER).glob("*.txt")]
    last_log = -1
    for name in log_files:
        num = int(name[name.find("log")+3 : name.find(".txt")])
        if num > last_log:
            last_log = num

    return last_log

##########################################################
##########################################################
##########################################################
