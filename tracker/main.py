import socket
import threading
import sys
import json


from utils.logger import setup_logger
from tracker_core import Tracker


if __name__ == "__main__":
    setup_logger()
    tracker = Tracker()
    tracker.start()
