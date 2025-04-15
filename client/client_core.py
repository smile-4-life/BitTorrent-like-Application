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
from utils.error import HandleError

from state.leecher_choke import LeecherState
from state.seeder_choke import SeederState

from modules.handshake import Handshake
from modules.leeching import Leeching
from modules.choking import Choking

from handler.handshake_handler import HandleHandshake
from handler.interested_handler import HandleInterested
from handler.choking_handler import HandleChoking
from handler.request_handler import HandleRequest
from handler.piece_handler import HandlePiece
from handler.base_handler import HandshakeHandler, InterestedHandler, ChokedHandler, UnchokedHandler, RequestHandler, PieceHandler


CONFIG_PATH = os.path.join("config", "client_config.json")


class Client(Observer, Subject):
    def __init__(self):

        self.id = generate_peer_id()
        logging.info(f"My ID: {self.id}")

        self.ip = '0.0.0.0'  # should connect with tracker to get public IP

        self.my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_sock.bind(('0.0.0.0', 0))
        self.port = self.my_sock.getsockname()[1]
        logging.info(f"My port: {self.port}")

        self.Tracker_connection = HandleTracker()
        self.Peer_connection = HandlePeer()
        self.Peer_manager = PeerManager(self.id)
        self.Peer_factory = PeerFactory()
        self.Strategy_manager = StrategyManager()

        config = load_config(CONFIG_PATH)
        #self.port = config['client_port']
        
        self.Piece_manager = PieceManager( config )
        self.tracker_URL = self.Piece_manager.tracker_URL

        self.Choke_manager = ChokeManager(SeederState() if self.Piece_manager.pieces_left == 0 else LeecherState(), self.id)
        
        shared_args = (self.id, self.port, self.Piece_manager, self.Peer_manager, self.Peer_connection)

        self.Handshake_handler = HandleHandshake(*shared_args, self.Peer_factory)
        self.Interested_handler = HandleInterested(*shared_args)
        self.Request_handler = HandleRequest(*shared_args)

        self.command_dispatcher = {
            "HANDSHAKE": HandshakeHandler(self.Handshake_handler),
            "INTERESTED": InterestedHandler(self.Interested_handler),
            "REQUEST": RequestHandler(self.Request_handler),
        }

        self.Handshake_module = Handshake(*shared_args, self.Peer_factory)
        self.Choking_module = Choking(*shared_args, self.Choke_manager)
        self.Leeching_module = Leeching(*shared_args, self.Strategy_manager)

        self.stop_event = threading.Event()
        

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
            self.my_sock.listen(10)
            logging.info(f"Peer listener started on {self.ip}:{self.port}")

            with ThreadPoolExecutor(max_workers=10) as executor:
                while True:
                    client_sock, addr = self.my_sock.accept()
                    client_sock.settimeout(2.0)
                    logging.info(f"Connection from {addr}")
                    executor.submit(self._handle_connection, client_sock, addr[0])
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def _handle_connection(self, sock, peer_ip):
        try:
            while not self.stop_event.is_set():
                msg = self.Peer_connection.receive_message(sock)
                if msg == 0:
                    continue
                if msg == None:
                    return
        
                opcode = msg.get("opcode")
                if opcode == "DONE":
                    break
                handler = self.command_dispatcher.get(opcode)

                if handler:
                    handler.handle(sock, peer_ip, msg)
                else:
                    logging.warning(f"Unknown opcode {opcode} from {peer_ip}")
                    break
        except HandleError as e:
            logging.info(f"{e}")

        except OSError:
            if not sock.fileno() == -1:
                sock.close()
                logging.warning(f"Closed connection with {peer_ip} during _handle_connection.")
        except Exception as e:
            logging.error(f"Unexpected error in _handle_connection: {e}")
        finally:
            if not sock.fileno() == -1:
                sock.close()
                logging.info(f"Closed socket with {peer_ip}.")

# start

    def start(self):
        try:
            self.register()
            self.getlistpeer()
            self.start_listening()
            self.Handshake_module.start_handshake()
            self.Choking_module.start_loop_choking()
            self.Leeching_module.start_leeching()

            input()
            self.stop_event.set()
            self.unregister()
        except Exception as e:
            logging.error(f"Start-Client catched error: {e}")
