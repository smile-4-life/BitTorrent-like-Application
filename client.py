import socket
import json
import threading
import time
import random
import os
import logging

from utils.read_metainfo import *
from utils import loader
from utils.algorithm import *

logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt='%H:%M:%S',
        handlers=[
            #logging.FileHandler("client.log"), 
            logging.StreamHandler()  
        ]
    )

class TorrentClient:
    def __init__(self, config_path='config/clientConfig.json'):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.load_config(config_path)
        self.PEERS = {} # key:value - peer_addr:listpieces
        self.PIECES = {} # key:value - piece:bitfield
        self.DOWNLOADED = 0
        self.LEFT = 0

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            logging.error("❌ Config file '{config_path}' not found.")
            exit(1)

        with open(config_path, 'r') as f:
            config = json.load(f)

        self.metainfo_file_path = config.get('metainfo_file_path', "metainfo.torrent")
        self.client_port = config.get('client_port', 9001)

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

    def start(self):
        self.register()
    
    def register(self):
        tracker_IP, tracker_port = self.tracker_URL.split(':')
        tracker_port = int(tracker_port)
        try:    
            self.sock.connect((tracker_IP, tracker_port))
            logging.info("connected to tracker")
        except Exception as e:
            logging.error(f"Error to register: {e}")

if __name__ == "__main__":
    file_name = f"file-{random.randint(1000, 9999)}.txt"
    client = TorrentClient()
    client.register()
    #client.start()
