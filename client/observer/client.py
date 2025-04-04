import logging
import json
import threading
import os

from observer.peer_factory import PeerFactory
from connection.tracker_connection import HandleTracker
from utils.load_config import load_config
from utils.torrent_reader import TorrentReader

CONFIG_PATH = "config\\client_config.json"

class ClientObserver:
    def __init__(self):

        self.ip = '127.0.0.1'

        self.peers = []
        self.Factory = PeerFactory()

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
        self._getlistpeer()

    def register(self):
        tracker_connect = HandleTracker()
        tracker_connect.send_register_request(self.tracker_URL, self.port,  self.pieces_left)

    def unregister(self):
        tracker_connect = HandleTracker()
        tracker_connect.send_unregister_request()

    def _getlistpeer(self):
        tracker_connect = HandleTracker()
        peer_list = tracker_connect.request_list_peers(self.tracker_URL)
        if peer_list == None:
            logging.info(f"No peers found in network.")
            return
        for peer in peer_list:
            new_peer = self.Factory.new_peer(peer['ip'], peer['port'])

            if new_peer.ip == self.ip and new_peer.port == self.port:
                continue
            elif new_peer not in self.peers:
                self.peers.append(new_peer)
                logging.info(f"Added new peer: {new_peer.ip}:{new_peer.port}")
            else:
                logging.info(f"ALready have peer {new_peer.ip}:{new_peer.port}.")

    def _scan_downloaded_pieces(self):
        existing_pieces = os.listdir(self.download_folder_path)
        for file in existing_pieces:
            if file.endswith('.bin'):
                piece_hash = file[:-4]
                self.piece_bitfield[piece_hash] = 1
                self.pieces_left -= 1

    
                