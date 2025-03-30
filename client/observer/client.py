import logging
import json

from utils.load_config import load_config
from connection.client_handler import HandleTracker
from utils.metainfo_utils import read_torrent_file

MY_IP = "127.0.0.2"
CONFIG_PATH = "config\\client_config.json"

class ClientObserver:
    def __init__(self):

        config = load_config(CONFIG_PATH)
        self.metainfo_file_path = config['metainfo_file_path']
        self.myPort = config['client_port']
    
        (
            self.hash_dict, 
            self.tracker_URL, 
            self.file_name, 
            self.piece_length, 
            self.pieces, 
            self.file_length, 
            self.pieces_count ) = read_torrent_file(self.metainfo_file_path)

    def register_peer(self):
        handler = HandleTracker(self)
        sock = handler.connect_to_tracker(self.tracker_URL)
        response = handler.send_register_request(sock, MY_IP, self.myPort)
        logging.info(f"Response: {response}")
        sock.close()

    def unregister(self):
        send_unregister_request(self.tracker_url, self.client_ip, self.client_port)
