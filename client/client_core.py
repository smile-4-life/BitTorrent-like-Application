import logging
import json
import threading
import os
import socket
import hashlib

from concurrent.futures import ThreadPoolExecutor

from cores.observer_base import Observer
from cores.subject_base import Subject

from factory.peer_factory import PeerFactory

from manager.peer_manager import PeerManager
from manager.piece_manager import PieceManager

from connection.tracker_connection import HandleTracker
from connection.peer_connection import HandlePeer

from utils.load_config import load_config
from utils.torrent_reader import TorrentReader

CONFIG_PATH = "config\\client_config.json"

class Client(Observer, Subject):
    def __init__(self):
        self.Peer_manager = PeerManager()
        self.Factory = PeerFactory()

        config = load_config(CONFIG_PATH)
        self.port = config['client_port']

        self.Piece_manager = PieceManager( config )
        self._scan_downloaded_pieces()

        self.tracker_URL = self.Piece_manager.tracker_URL
        self.ip = '0.0.0.0'  # should connect with tracker to get public IP

    def _scan_downloaded_pieces(self):
        self.Piece_manager.scan_downloaded_pieces()

    #=====Observer Parttern=====
    def attach(self, observer):
        self.Peer_manager.add_peer(observer)

    def detach(self, observer):
        self.Peer_manager.remove_peer(observer)

    def notify(self, data):
        for peer in self.Peer_manager.get_all_peers():
            peer.update(peer.ip, peer.port, data)

    def update(self, ip, port, data):
        Peer_handler = HandlePeer()
        sock = Peer_handler.connect_to_peer(ip, port)
        Peer_handler.send_have(sock, data)

    #=====Core=====
    def start(self):
        try:
            self._register()
            self._getlistpeer()
            self.start_listening()
            self.request_missing_pieces()
            self._unregister()
        except Exception as e:
            logging.error(f"Start-Client catched error: {e}")

    def _register(self):
        tracker_connect = HandleTracker()
        self.ip = tracker_connect.send_register_request(self.tracker_URL, self.port, self.Piece_manager.pieces_left)

    def _unregister(self):
        tracker_connect = HandleTracker()
        tracker_connect.send_unregister_request(self.tracker_URL, self.port)

    def _getlistpeer(self):
        tracker_connect = HandleTracker()
        peer_list = tracker_connect.request_list_peers(self.tracker_URL)
        if peer_list is None:
            logging.info("No peers found in network.")
            return
        for peer in peer_list:
            new_peer = self.Factory.new_peer(peer['ip'], peer['port'])

            if new_peer.ip == self.ip and new_peer.port == self.port:
                continue
            elif not self.Peer_manager.has_peer(new_peer):
                self.attach(new_peer)
                logging.info(f"Added new peer: {new_peer.ip}:{new_peer.port}")
            else:
                logging.info(f"Already have peer {new_peer.ip}:{new_peer.port}.")

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

# method tạm thời
    def request_missing_pieces(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._request_from_peer, peer) for peer in self.Peer_manager.get_all_peers()]
            for future in futures:
                future.result()

    def _request_from_peer(self, peer):
        peer_handler = HandlePeer()
        try:
            sock = peer_handler.connect_to_peer(peer.ip, peer.port)
            for piece_index in self.Piece_manager.get_missing_piece_indexes():
                peer_handler.send_request(sock, piece_index)
                piece_data, speed = peer_handler.receive_piece(sock)
                self.Peer_manager.update_download_speed(peer, speed)
                if self.Piece_manager.verify_and_save(piece_data['piece_index'], piece_data['data']):
                    self.notify({'event': 'piece_downloaded', 'index': piece_data['piece_index']})
            sock.close()
        except Exception as e:
            logging.error(f"Error requesting pieces from peer {peer.ip}:{peer.port} - {e}")
