import sys
import os

from subject.tracker import *

def start_tracker():
    print(f"[Tracker] Loaded config: {config}")
    print("[Tracker] Running...")

if __name__ == "__main__":
    tracker = TorrentTracker()
    tracker.start()
