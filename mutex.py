from threading import Lock
from weakref import WeakValueDictionary


class Mutex:
    """Provides an RAII mutex for any ID based group of entities"""
    # Main lock for protecting locks for the individual locks
    general_lock = Lock()
    
    # Map of IDs and their corresponding mutexes if they exist
    locks = WeakValueDictionary()

    def __init__(self, id) -> None:
        Mutex.general_lock.acquire()

        # Check if there is a lock for this user
        if id in Mutex.locks:
            self.m = Mutex.locks[id]
        else: # Otherwise create a new lock
            self.m = Lock()
            Mutex.locks[id] = self.m

        self.m.acquire()

        Mutex.general_lock.release()

    def __del__(self):
        """Release lock upon destruction of the object"""
        if self.m.locked():
            self.m.release()

    def unlock(self):
        """Unlock the underlying lock; shouldn't be used"""
        self.m.release()
