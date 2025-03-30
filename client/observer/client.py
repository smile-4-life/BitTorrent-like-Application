import logging
import json
from connection.client_handler import connect_to_tracker, send_register_request, send_unregister_request, send_hash_list
from utils.metainfo_utils import read_torrent_file

class ClientObserver:
    def __init__(self, client_ip, client_port, tracker_url):
        self.client_ip = client_ip
        self.client_port = client_port
        self.tracker_url = tracker_url
        self.hash_dict = {}

    def register_peer(self):
        """Register the client with the tracker and return its assigned address."""
        tracker_socket = connect_to_tracker(self.tracker_url)
        if tracker_socket is None:
            return None

        try:
            this_addr = send_register_request(tracker_socket, self.client_ip, self.client_port)
            if this_addr:
                send_hash_list(tracker_socket, self.hash_dict)
            return this_addr
        finally:
            tracker_socket.close()

    def unregister(self):
        """Unregister the client from the tracker."""
        send_unregister_request(self.tracker_url, self.client_ip, self.client_port)
