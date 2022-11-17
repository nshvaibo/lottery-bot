from threading import Lock, RLock
from weakref import WeakValueDictionary

class MutexRAII:
    def __init__(self) -> None:
        self.m = Lock()

    def __del__(self):
        """Release lock upon destruction of the object"""
        if self.m.locked():
            self.m.release()

class LockGenerator:
    """Provides an RAII mutex for any ID based group of entities"""

    def __init__(self) -> None:
        # Main lock for protecting locks for the individual locks
        self.general_lock = Lock()
        
        # Map of IDs and their corresponding mutexes if they exist
        self.locks = WeakValueDictionary()
    
    def get_lock(self, id, read_only=False):
        """Returns a lock for this entity in the group when shared state can be accessed"""
        self.general_lock.acquire()

        # Check if there is a lock for this user
        if id in self.locks:
            lock = self.locks[id]
        else: # Otherwise create a new lock
            lock = Lock() if not read_only else RLock()
            self.locks[id] = lock

        lock.acquire()

        self.general_lock.release()

        return lock
