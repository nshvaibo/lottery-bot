"""Manipulation of client data: wallet, lottery tickets"""
from copy import deepcopy
from threading import Lock
from weakref import WeakValueDictionary

from db import db, firestore


class Mutex:
    """Provides an RAII mutex for each user"""
    # Mutex for protecting locks for each individual user
    user_lock = Lock()
    
    # Map of user IDs to their corresponding mutexes if they exist
    locks = WeakValueDictionary()

    def __init__(self, user_id) -> None:
        Mutex.user_lock.acquire()

        # Check if there is a lock for this user
        if user_id in Mutex.locks:
            self.m = Mutex.locks[user_id]
        else: # Otherwise create a new lock
            self.m = Lock()
            Mutex.locks[user_id] = self.m

        self.m.acquire()

        Mutex.user_lock.release()

    def __del__(self):
        """Release lock upon destruction of the object"""
        if self.m.locked():
            self.m.release()

    def unlock(self):
        """Unlock the underlying lock; shouldn't be used"""
        self.m.release()

class User:
    def __init__(self, user_id: int) -> None:
        lock = Mutex(user_id)

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
        lock = Mutex(self.id)
        return self._first_time_user

    def get_balance(self) -> float:
        """Returns current user balance"""
        lock = Mutex(self.id)
        
        return self.state["balance"]

    
    def add_balance(self, amount):
        """
        Adds <amount> to the balance
        ### Returns:
        New balance: float
        """
        lock = Mutex(self.id)
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
        lock = Mutex(self.id)
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

    # def get_language(self) -> str:
    #     """
    #     Returns user language. Possible values:
    #     * en
    #     * ru
    #     """
    #     lock = Mutex(self.id)
        
    #     return self.state["lang"]

    # def set_language(self, lang: str) -> str:
    #     """
    #     Updates the value of user language in the database
    #     :param lang: Language of the user. Possible values: <"en", "ru">
    #     :type lang: str
    #     """
    #     lock = Mutex(self.id)
    #     doc_ref = self._doc_ref()

    #     # Update balance in the database
    #     doc_ref.update({"lang": lang})

    #     # Update balance locally
    #     self.state["lang"] = lang
