"""Operations on user tickets"""
from db import db
from lock_generator import LockGenerator

lock_generator = LockGenerator()

class Referrals:
    def _doc_ref(self, ref_code: str):
        """Returns Firestore document reference of this referral code"""
        return db.collection("referrals").document(ref_code)
    
    def get_user_id(self, ref_code):
        """Returns a dict of (ticket_number, user_id)"""
        lock = lock_generator.get_lock("referrals", read_only=True)

        doc_ref = self._doc_ref(ref_code)
        referral_from = doc_ref.get()
        if referral_from.exists:
            return True, referral_from.to_dict()["user_id"]
        else:
            return False, -1

    def add_referral(self, ref_code, user_id):
        """
            Creates a new referral in the database
            * ref_code: unique referral code of a user
            * user_id: corresponding user id of this user
        """
        lock = lock_generator.get_lock("referrals")

        doc_ref = self._doc_ref(ref_code)
        doc_ref.set({"user_id": user_id})
