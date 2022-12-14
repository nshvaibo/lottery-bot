"""Manipulation of client data: wallet, lottery tickets"""
from copy import deepcopy

from config import TICKET_PRICE_TON
from db import db, firestore
from lock_generator import LockGenerator

lock_generator = LockGenerator()

class User:
    def __init__(self, user_id) -> None:
        lock = lock_generator.get_lock(user_id)

        # Unique user id defined by Telegram
        self.id = user_id

        # Assume an existing user
        self._first_time_user = False

        # Attempt to retrieve user data from the database
        user_state = self._retrieve_user()

        # Check whether this user exists
        if user_state is None:
            # Initialize new user's state to default values
            user_state = {
                "balance": float(0),
                "tickets": [],
                # "lang": lang,
                "last_active": firestore.SERVER_TIMESTAMP
            }

            self._first_time_user = True

            # Upload state to the database
            doc_ref = self._doc_ref()
            doc_ref.set(user_state)

        self.state = user_state

    def _retrieve_user(self):
        """
        Returns user data from the database if the user exists, None otherwise
        Updates the timestamp when the user was last active
        Assumes a lock is held to protect user data
        """
        # Retrieve user data
        doc_ref = self._doc_ref()
        user = doc_ref.get()

        if user.exists:
            doc_ref.update({"last_active": firestore.SERVER_TIMESTAMP})

        return user.to_dict()

    def _to_dict(self):
        return deepcopy(self.state)

    def _doc_ref(self):
        """Returns Firestore document reference to this user's db file"""
        return db.collection("users").document(str(self.id))

    def is_first_time_user(self):
        """Return True if the user is not registered with the bot"""
        lock = lock_generator.get_lock(self.id)
        return self._first_time_user

    def get_balance(self) -> float:
        """Returns current user balance"""
        lock = lock_generator.get_lock(self.id)
        
        return self.state["balance"]

    
    def add_balance(self, amount):
        """
        Adds <amount> to the balance
        ### Returns:
        New balance: float
        """
        lock = lock_generator.get_lock(self.id)
        doc_ref = self._doc_ref()

        new_balance = self.state["balance"] + amount

        # Update balance in the database
        doc_ref.update({"balance": new_balance})

        # Update balance locally
        self.state["balance"] = new_balance

    def withdraw_balance(self, amount) -> bool:
        """
        Withdraw <amount> to the balance
        ### Returns:
        (Success: bool, New balance: float)
        """
        lock = lock_generator.get_lock(self.id)
        doc_ref = self._doc_ref()

        # Can only withdraw at most how much is on the balance
        cur_balance = self.state["balance"]
        if cur_balance - amount < 0:
            return False

        new_balance = cur_balance - amount

        # Update balance in the database
        doc_ref.update({"balance": new_balance})

        # Update balance locally
        self.state["balance"] = new_balance

        return True

    def get_tickets(self):
        """Returns a list of ticket numbers purchased by the user"""
        lock = lock_generator.get_lock(self.id)
    
        return self.state["tickets"]

    def purchase_ticket(self, ticket_num) -> bool:
        """Returns a list of ticket numbers purchased by the user"""
        lock = lock_generator.get_lock(self.id)

        # Connect to the database
        doc_ref = self._doc_ref()

        # Make sure that the user has enough funds to purchase the ticket
        if TICKET_PRICE_TON > self.state["balance"]:
            return False

        # Add new ticket and update balance in the database
        doc_ref.update({
            "tickets": firestore.ArrayUnion([ticket_num]),
            "balance": self.state["balance"] - TICKET_PRICE_TON
        })

        # Update balance locally
        self.state["balance"] -= TICKET_PRICE_TON

        # Add new ticket locally
        self.state["tickets"].append(ticket_num)

        return True

    def remove_tickets(self) -> bool:
        """Deletes all tickets that the user has"""
        lock = lock_generator.get_lock(self.id)

        # Connect to the database
        doc_ref = self._doc_ref()

        # Add new ticket and update balance in the database
        doc_ref.update({
            "tickets": []
        })

        # Remove ticket locally
        self.state["tickets"] = []

        return True
