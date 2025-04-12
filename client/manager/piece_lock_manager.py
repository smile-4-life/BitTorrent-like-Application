from collections import defaultdict
from threading import Lock

class PieceLockManager:
    def __init__(self):
        self.locks = defaultdict(Lock)

    def get_lock(self, piece_index):
        return self.locks[piece_index]

Lock_manager = PieceLockManager()