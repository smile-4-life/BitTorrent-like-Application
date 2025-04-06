from collections import defaultdict
from threading import Lock

class PieceLockManager:
    def __init__(self):
        self.locks = defaultdict(Lock)

    def get_lock(self, piece_hash):
        return self.locks[piece_hash]

lock_manager = PieceLockManager()