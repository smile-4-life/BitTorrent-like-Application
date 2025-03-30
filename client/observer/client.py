import socket
import json
import threading
import time
import random
import os
import logging

from utils.metainfo_utils import *

from state.client_state import *

from connection.tracker_client_connection import *

class TorrentClient:
    def __init__(self, config_path='config/client_config.json'):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.load_config(config_path)
        self.PEERS = {} # key:value - peer_addr:listpieces
        self.PIECES = {} # key:value - piece:bitfield
        self.DOWNLOADED = 0
        self.LEFT = 0

        self.state = IdleState(self)

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            logging.error("❌ Config file '{config_path}' not found.")
            exit(1)

        with open(config_path, 'r') as f:
            config = json.load(f)

        self.metainfo_file_path = config.get('metainfo_file_path', "metainfo.torrent")
        self.client_port = config.get('client_port', 0)

        (
            self.hash_dict,
            self.tracker_URL,
            self.file_name,
            self.piece_length,
            self.pieces,
            self.file_length,
            self.pieces_count
        ) = read_torrent_file(self.metainfo_file_path)
        
        logging.debug("✅ Loaded config: {config}")

    def change_state(self, new_state):
        logging.info(f"State changed to: {new_state.__class__.__name__}")
        self.state = new_state

    def start(self):
        self.register()
    
    def register(self):
        self.state.connect_to_tracker()
