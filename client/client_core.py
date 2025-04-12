import logging
import json
import threading
import os
import socket
import hashlib
import time

from protocol.peer_protocol import *

from concurrent.futures import ThreadPoolExecutor

from cores.observer_base import Observer
from cores.subject_base import Subject

from factory.peer_factory import PeerFactory

from manager.peer_manager import PeerManager
from manager.piece_manager import PieceManager
from manager.choke_manager import ChokeManager
from manager.strategy_manager import StrategyManager

from connection.tracker_connection import HandleTracker
from connection.peer_connection import HandlePeer

from utils.load_config import load_config
from utils.torrent_reader import TorrentReader
from utils.generate_id import generate_peer_id

from state.leecher_choke import LeecherState
from state.seeder_choke import SeederState

from handler.handshake import Handshake
from handler.seeding import Seeding
from handler.leeching import Leeching
from handler.choking import Choking

CONFIG_PATH = "config\\client_config.json"

class Client(Observer, Subject):
    def __init__(self):
        self.Tracker_connection = HandleTracker()
        self.Peer_connection = HandlePeer()
        self.Peer_manager = PeerManager()
        self.Peer_factory = PeerFactory()
        self.Strategy_manager = StrategyManager()

        self.id = generate_peer_id()
        self.ip = '0.0.0.0'  # should connect with tracker to get public IP
        self.port = int(input("Enter port: "))

        config = load_config(CONFIG_PATH)
        #self.port = config['client_port']
        
        self.Piece_manager = PieceManager( config )
        self.tracker_URL = self.Piece_manager.tracker_URL

        self.Choke_manager = ChokeManager(SeederState() if self.Piece_manager.pieces_left == 0 else LeecherState(), self.id)
        
        shared_args = (self.id, self.port, self.Piece_manager, self.Peer_manager, self.Peer_connection)

        self.Handshake_handler = Handshake(*shared_args, self.Peer_factory)
        self.Leeching_handler = Leeching(*shared_args, self.Strategy_manager)
        self.Seeding_handler = Seeding(*shared_args)
        self.Choking_handler = Choking(*shared_args, self.Choke_manager)

            #=====Observer Parttern=====

    def attach(self, observer):
        self.Peer_manager.add_peer(observer)

    def detach(self, observer):
        self.Peer_manager.remove_peer(observer)

    def notify(self, data):
        pass

    def update(self, ip, port, data):
        sock = self.Peer_connection.connect_to_addr(ip, port)
        self.Peer_connection.send_have(sock, data)

            #=====TRACKER=====
    def register(self):
        self.ip = self.Tracker_connection.send_register_request(self.tracker_URL, self.port, self.Piece_manager.pieces_left)

    def unregister(self):
        self.Tracker_connection.send_unregister_request(self.tracker_URL, self.port)

    def getlistpeer(self):
        peer_list = self.Tracker_connection.request_list_peers(self.tracker_URL)
        if peer_list is None:
            logging.info("No peers found in network.")
            return
        for addr_dict in peer_list:
            ip = addr_dict.get("ip")
            port = addr_dict.get("port")
            addr = (ip,port)
            if ip != self.ip or port != self.port:
                self.Peer_manager.add_raw_addr(addr)

    #=====  CLIENT  =====
    def start_listening(self):
        listener_thread = threading.Thread(target=self._listen)
        listener_thread.daemon = True
        listener_thread.start()

    def _listen(self):
        try:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind(('0.0.0.0', self.port))
            #server_sock.bind((self.ip, self.port))
            server_sock.listen(10)
            logging.info(f"Peer listener started on {self.ip}:{self.port}")

            with ThreadPoolExecutor(max_workers=10) as executor:
                while True:
                    client_sock, addr = server_sock.accept()
                    logging.info(f"Connection from {addr}")
                    executor.submit(self._handle_connection, client_sock, addr[0])
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def _handle_connection(self, sock, peer_ip):
        try:
            while True:
                msg = self.Peer_connection.receive_message(sock)
                if not msg:
                    return
        
                opcode = msg.get("opcode")

                if opcode == "HANDSHAKE":
                    self.Handshake_handler._handle_handshake(sock, peer_ip, msg)
                    sock.close()
                    break
                if opcode == "INTERESTED":
                    self.Seeding_handler.handle_interested(sock, peer_ip, msg)
                    sock.close()
                    break
                if opcode == "CHOKED":
                    self._handle_choked(sock, peer_ip, msg)
                    sock.close()
                    break
                if opcode == "UNCHOKED":
                    self._handle_unchoked(sock, peer_ip, msg)
                    sock.close()
                    break
        except Exception as e:
            logging.error(f"Unexpected error in _handle_connection: {e}")

# start

    def start(self):
        try:
            self.register()
            self.getlistpeer()
            self.start_listening()
            self.Handshake_handler.start_handshake()
            self.Choking_handler.start_loop_choking()
            self.Leeching_handler.start_leeching()

            input()
            self.unregister()
        except Exception as e:
            logging.error(f"Start-Client catched error: {e}")
