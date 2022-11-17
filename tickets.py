"""Operations on user tickets"""
from datetime import date, datetime, timezone

from db import db, firestore
from lock_generator import LockGenerator

lock_generator = LockGenerator()

class Tickets:
    def __init__(self, lottery: str) -> None:
        """<lottery> can be either \"daily\" or \"weekly\""""
        self.lottery = lottery

    def _subcollection_ref(self):
        """Returns Firestore reference to the subcollection of tickets corresponding to today's lottery"""
        today = datetime.now(timezone.utc).date().strftime("%d.%m.%Y")
        return db.collection(f"tickets_{self.lottery}").document(today).collection("tickets")
    
    def get_all(self):
        """Returns a dict of (ticket_number, user_id)"""
        lock = lock_generator.get_lock(self.lottery, read_only=True)

        tickets_ref = self._subcollection_ref()
        tickets = {}
        for doc in tickets_ref.stream():
            tickets[doc.id] = doc.to_dict()["user_id"]

        return tickets

    def add_tickets(self, tickets: list, user_id):
        """Add new tickets purchased by a user"""
        lock = lock_generator.get_lock(self.lottery)

        tickets_ref = self._subcollection_ref()
        writer = db.bulk_writer()

        for ticket in tickets:
            doc_ref = tickets_ref.document(str(ticket))
            
            writer.set(doc_ref, {"user_id": user_id})

        writer.close()
