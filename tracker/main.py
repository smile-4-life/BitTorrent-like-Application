import socket
import threading
import sys
import json


from utils.logger import setup_logger
from subject.tracker import TrackerSubject


if __name__ == "__main__":
    setup_logger()
    tracker = TrackerSubject()
    tracker.start()
