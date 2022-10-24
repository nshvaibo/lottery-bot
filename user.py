"""Manipulation of client data: wallet, lottery tickets"""
import json

from db import db


def is_known(user_id):
    """Returns True if <user_id> is an existing user of the bot"""
    doc_ref = db.collection(u"users").document(str(user_id))

    doc = doc_ref.get()
    if doc.exists:
        print(f'Document data: {doc.to_dict()}')
    else:
        print(u'No such document!')

def add_user(user_id):
    """Initialize state for a new user"""
    f = open("db.json", "r")
    db = json.load(f)
    f.close()

    f = open("db.json", "w")
    db["known_users"].append(user_id)
    json.dump(db, f)
    f.close()
