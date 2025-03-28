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
        self.state = {
            'PEERS': {},        # key: peer_addr, value: listpieces
            'PIECES': {},       # key: piece, value: bitfield
            'DOWNLOADED': 0,    # piece đã tải
            'LEFT': 0           # piece còn lại
        }
        self.load_config(config_path)

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            logging.error(f"❌ Config file '{config_path}' not found.")
            exit(1)

        with open(config_path, 'r') as f:
            config = json.load(f)

        self.metainfo_file_path = config.get('metainfo_file_path', 'metainfo.torrent')
        self.client_port = config.get('client_port', 8080)

        try:
            (
                self.hash_dict,
                self.tracker_URL,
                self.file_name,
                self.piece_length,
                self.pieces,
                self.file_length,
                self.pieces_count
            ) = read_torrent_file(self.metainfo_file_path)

            logging.info(f"✅ Loaded config from '{config_path}':")
            logging.info(f"   - Metainfo file: {self.metainfo_file_path}")
            logging.info(f"   - Client port: {self.client_port}")
            logging.info(f"   - File name: {self.file_name}, Size: {self.file_length} bytes")
            logging.info(f"   - Pieces: {self.pieces_count}, Piece length: {self.piece_length} bytes")

        except Exception as e:
            logging.error(f"❌ Error loading torrent file: {e}")
            exit(1)

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
