import logging
import json
import threading
import os
import socket

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from cores.observer_base import Observer
from cores.subject_base import Subject

from factory.peer_factory import PeerFactory
from connection.tracker_connection import HandleTracker
from utils.load_config import load_config
from utils.torrent_reader import TorrentReader

CONFIG_PATH = "config\\client_config.json"

class Client(Observer, Subject):
    def __init__(self):
        
        self.peers_lock = Lock()
        self.piece_lock = Lock()
        self.bitfiled_lock = Lock()


        self.ip = '0.0.0.0' #should connect with tracker to get public IP

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
            self.list_pieces,  #lock
            self.file_length, 
            self.pieces_left   #lock
            ) = reader.read_torrent_file(self.metainfo_file_path)

        self.piece_bitfield = {piece:0 for piece in self.list_pieces}
        self._scan_downloaded_pieces()

    
    # ===== Utils func =====
    def _scan_downloaded_pieces(self):
        existing_pieces = os.listdir(self.download_folder_path)
        for file in existing_pieces:
            if file.endswith('.bin'):
                piece_hash = file[:-4]
                self.piece_bitfield[piece_hash] = 1
                self.pieces_left -= 1


    # ===== Observer Pattern =====
    def attach(self, observer):
        self.peers.append(observer)

    def detach(self, observer):
        self.peers.remove(observer)

    def notify(self, data):
        pass

    def update(self,data):
        pass

    
    # ===== Start =====
    def start(self):
        try:
            self._register()
            self._getlistpeer()
            self.start_listening()
            self.request_missing_pieces()
            self._unregister()
        except Exception as e:
            logging.error(f"Start-Client catched error: {e}")

    # ===== Method - Tracker =====

    def _register(self):
        tracker_connect = HandleTracker()
        self.ip = tracker_connect.send_register_request(self.tracker_URL, self.port, self.pieces_left)

    def _unregister(self):
        tracker_connect = HandleTracker()
        tracker_connect.send_unregister_request(self.tracker_URL, self.port)

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
                self.attach(new_peer)
                logging.info(f"Added new peer: {new_peer.ip}:{new_peer.port}")
            else:
                logging.info(f"ALready have peer {new_peer.ip}:{new_peer.port}.")

    # ===== with client =====
    def start2(self):
        try:
            self.start_listening()
            self.request_missing_pieces()
        except Exception as e:
            logging.error(f"Start2-Client catched error: {e}")

    def start_listening(self):
        listener_thread = threading.Thread(target=self._listen_for_peer_requests)
        listener_thread.daemon = True
        listener_thread.start()

    def _listen_for_peer_requests(self):
        try:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind((self.ip, self.port))
            server_sock.listen(10)
            logging.info(f"Peer listener started on {self.ip}:{self.port}")

            with ThreadPoolExecutor(max_workers=10) as executor:
                while True:
                    client_sock, addr = server_sock.accept()
                    executor.submit(self._handle_peer_connection, client_sock)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def _handle_peer_connection(self, sock):
        peer_handler = HandlePeer()
        peer_handler.listen_for_requests(sock)

    def request_missing_pieces(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._request_from_peer, peer) for peer in self._get_peers_threadsafe()]
            for future in futures:
                future.result()

    def _request_from_peer(self, peer):
        peer_handler = HandlePeer()
        try:
            sock = peer_handler.connect_to_peer(peer.ip, peer.port)
            for piece_hash in self.list_pieces:
                if not self._has_piece(piece_hash):
                    peer_handler.send_request(sock, piece_hash)
                    piece_data = peer_handler.receive_piece(sock)
                    self._save_piece(piece_data['piece_index'], piece_data['data'])
                    self.notify({'event': 'piece_downloaded', 'index': piece_data['piece_index']})
            sock.close()
        except Exception as e:
            logging.error(f"Error requesting pieces from peer {peer.ip}:{peer.port} - {e}")

    def _has_piece(self, piece_hash):
        with self.bitfield_lock:
            return self.piece_bitfield.get(piece_hash) == 1

    def _save_piece(self, piece_index, data):
        piece_path = os.path.join(self.download_folder_path, "list_pieces", f"{piece_index}.bin")
        with self.piece_lock:
            with open(piece_path, 'wb') as f:
                f.write(data)
        with self.bitfield_lock:
            self.piece_bitfield[piece_index] = 1
            self.pieces_left -= 1

    def _get_peers_threadsafe(self):
        with self.peers_lock:
            return list(self.peers)
