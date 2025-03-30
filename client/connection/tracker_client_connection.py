import socket
import logging

class ClientTracker:    
    def __init__(self, client:object):
        self.client = client

    def register(self):
        tracker_IP, tracker_port = self.client.tracker_URL.split(':')
        tracker_port = int(tracker_port)
        try:    
            self.client.sock.connect((tracker_IP, tracker_port))
            logging.info("Connected to Tracker")
        except Exception as e:
            logging.error(f"Error to register: {e}")
    