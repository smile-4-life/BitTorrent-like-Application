import logging
import json
import threading
import os

from utils.load_config import load_config
from connection.tracker_connection import HandleTracker
from utils.metainfo_utils import read_torrent_file

CONFIG_PATH = "config\\client_config.json"

class ClientObserver:
    def __init__(self):

        config = load_config(CONFIG_PATH)
        self.port = config['client_port']
        self.metainfo_file_path = config['metainfo_file_path']
        self.download_folder_path = config['download_folder_path']
    
        (
            self.tracker_URL, 
            self.file_name, 
            self.piece_length, 
            self.list_pieces, 
            self.file_length, 
            self.pieces_count ) = read_torrent_file(self.metainfo_file_path)
        
        self.piece_bitfield = {piece_ : 0 for piece_ in self.list_pieces} #defaut bit-filed 0 
        self.bit_field_lock = threading.Lock()

        #self.bit_field = lambda piece_: { piece_: 0 for piece_ in pieces }

    def start(self):
        self.update_downloaded_pieces()
        self.register()

    def register(self):
        list_pieces = [piece for piece in self.client_observer.piece_bitfield.keys() if self.client_observer.piece_bitfield[piece]]

        tracker_connect = HandleTracker()
        tracker_connect.send_register_request(list_pieces)

    def unregister(self):
        tracker_connect = HandleTracker()
        tracker_connect.send_unregister_request()

    def update_downloaded_pieces(self):
        existing_pieces = os.listdir(self.download_folder_path)
        for file in existing_pieces:
            if file.endswith('.bin'):
                piece_hash = file[:-4]
                self.piece_bitfield[piece_hash] = 1
                