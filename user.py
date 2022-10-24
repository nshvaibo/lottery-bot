"""Manipulation of client data: wallet, lottery tickets"""
import json

def is_known(user_id):
    """Returns True if <user_id> is an existing user of the bot"""
    f = open("db.json", "r")
    db = json.load(f)
    f.close()

    return user_id in db["known_users"]

def add_user(user_id):
    """Initialize state for a new user"""
    f = open("db.json", "r")
    db = json.load(f)
    f.close()

    f = open("db.json", "w")
    db["known_users"].append(user_id)
    json.dump(db, f)
    f.close()
