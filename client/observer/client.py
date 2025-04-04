import logging
import json
import threading
import os

from connection.tracker_connection import HandleTracker
from utils.load_config import load_config
from utils.torrent_reader import TorrentReader

CONFIG_PATH = "config\\client_config.json"

class ClientObserver:
    def __init__(self):

        config = load_config(CONFIG_PATH)
        self.port = config['client_port']
        self.metainfo_file_path = config['metainfo_file_path']
        self.download_folder_path = config['download_folder_path']

        reader = TorrentReader()
        (
            self.tracker_URL, 
            self.file_name, 
            self.piece_length, 
            self.list_pieces, 
            self.file_length, 
            self.pieces_left ) = reader.read_torrent_file(self.metainfo_file_path)
        
        '''
        self.piece_bitfield = {piece_ : 0 for piece_ in self.list_pieces}   #defaut bit-filed 0 
        self.bit_field_lock = threading.Lock()
        '''

    def start(self):
        self._scan_downloaded_pieces()
        self.register()

    def register(self):
        tracker_connect = HandleTracker()
        tracker_connect.send_register_request(self.tracker_URL, self.port,  self.pieces_left)

    def unregister(self):
        tracker_connect = HandleTracker()
        tracker_connect.send_unregister_request()



    def _scan_downloaded_pieces(self):
        existing_pieces = os.listdir(self.download_folder_path)
        for file in existing_pieces:
            if file.endswith('.bin'):
                piece_hash = file[:-4]
                self.piece_bitfield[piece_hash] = 1
                self.pieces_left -= 1

    
                