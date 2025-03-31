import logging
import json

from utils.load_config import load_config
from connection.tracker_connection import HandleTracker
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
        tracker_connect = HandleTracker(self)
        tracker_connect.send_register_request()

    def unregister(self):
        tracker_connect = HandleTracker(self)
        tracker_connect.send_unregister_request()
