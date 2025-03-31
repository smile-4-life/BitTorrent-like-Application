import logging
import json

from utils.load_config import load_config
from connection.handle_tracker import HandleTracker
from utils.metainfo_utils import read_torrent_file

MY_IP = "127.0.0.2"
CONFIG_PATH = "config\\client_config.json"

class ClientObserver:
    def __init__(self):

        config = load_config(CONFIG_PATH)
        self.metainfo_file_path = config['metainfo_file_path']
        self.port = config['client_port']
    
        (
            self.hash_dict, 
            self.tracker_URL, 
            self.file_name, 
            self.piece_length, 
            self.pieces, 
            self.file_length, 
            self.pieces_count ) = read_torrent_file(self.metainfo_file_path)

    def start(self):
        self.register()

    def register(self):
        handler = HandleTracker(self)
        handler.send_register_request()

    def unregister(self):
        send_unregister_request(self.tracker_url, self.client_ip, self.client_port)
