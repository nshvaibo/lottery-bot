"""Operations on user tickets"""
from datetime import date, datetime, timezone, timedelta

from db import db, firestore
from lock_generator import LockGenerator
from config import LOTTERY_TIME

lock_generator = LockGenerator()

class Tickets:
    def __init__(self, lottery: str) -> None:
        """<lottery> can be either \"daily\" or \"weekly\""""
        self.lottery = lottery

    def _subcollection_ref(self, force_today=False):
        """Returns Firestore reference to the subcollection of tickets corresponding to today's lottery"""
        now = datetime.now(timezone.utc)
        draw_time = datetime.combine(now, LOTTERY_TIME, tzinfo=timezone.utc)

        if now > draw_time:
            day = now + timedelta(days=1)
        else:
            day = now

        if force_today:
            day = now
        
        day = now.date().strftime("%d.%m.%Y")
        return db.collection(f"tickets_{self.lottery}").document(day).collection("tickets")
    
    def get_all(self):
        """Returns a dict of (ticket_number, user_id)"""
        lock = lock_generator.get_lock(self.lottery, read_only=True)

        tickets_ref = self._subcollection_ref(force_today=True)
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
