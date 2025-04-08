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

CONFIG_PATH = "config\\client_config.json"

class Client(Observer, Subject):
    def __init__(self):
        self.Tracker_connection = HandleTracker()
        self.Peer_connection = HandlePeer()
        self.Peer_manager = PeerManager()
        self.Peer_factory = PeerFactory()
        self.Strategy_manager = StrategyManager()

        config = load_config(CONFIG_PATH)
        #self.port = config['client_port']
        self.port = int(input("Enter port: "))

        self.Piece_manager = PieceManager( config )
        self.Piece_manager.scan_downloaded_pieces()
        self.Choke_manager = ChokeManager(SeederState() if self.Piece_manager.pieces_left == 0 else LeecherState())

        self.tracker_URL = self.Piece_manager.tracker_URL
        self.ip = '0.0.0.0'  # should connect with tracker to get public IP
        self.id = generate_peer_id()


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
        while True:
            msg = self.Peer_connection.receive_message(sock)
            if not msg:
                return
    
            opcode = msg.get("opcode")

            if opcode == "HANDSHAKE":
                self._handle_handshake(sock, peer_ip, msg)
                sock.close()
                break
            if opcode == "INTERESTED":
                self._handle_interested(sock, peer_ip, msg)
                sock.close()
                break
            if opcode == "CHOKED":
                sock.close()
                print("CHOKED")
                break
            if opcode == "UNCHOKED":
                sock.close()
                print("UNCHOKED")
                break


    # ===== HANDSHAKE =====

    def _handle_handshake(self, sock, peer_ip, msg):
        try:
            peer_id = msg.get("peer_id")
            peer_port = msg.get("peer_port")
            new_peer = self._process_peer_handshake(peer_id, peer_ip, peer_port)
            
            reply_msg = self._build_handshake_msg()
            send_msg(sock, reply_msg)
            
            self._receive_and_update_bitfield(sock, new_peer)
            self._send_bitfield(sock)
        except Exception as e:
            logging.error(f"Unexpected error in _handshake: {e}")
        finally:
            print("Close handshake socket")
            sock.close()

    # ===== UTILS METHODS FOR HANDSHAKE

    def _process_peer_handshake(self, peer_id, peer_ip, peer_port):
        addr = (peer_ip, peer_port)
        self.Peer_manager.remove_raw_addr(addr)
        new_peer = self.Peer_factory.new_peer(peer_id, addr)
        self.Peer_manager.add_active_peer(new_peer)
        return new_peer

    def _build_handshake_msg(self):
        return encode_handshake(
                {
                "peer_id": self.id,
                "peer_port": self.port
                }
            )

    def _send_bitfield(self, sock):
        msg = {
            "str_bitfield": self.Piece_manager.get_str_bitfield()
        }
        bi_msg = encode_bitfield(msg)
        send_msg(sock, bi_msg)
    
    def _receive_and_update_bitfield(self, sock, peer):
        msg = self.Peer_connection.receive_message(sock)
        list_bitfield = msg.get("str_bitfield")
        self.Peer_manager.update_index_bitfield(peer, list_bitfield)

    # ===== INTERESTED =====

    def _handle_interested(self, sock, peer_ip, msg):
        peer_id = msg.get("peer_id")
        peer_port = msg.get("peer_port")
        
        if not self.unchoke_for_interested():
            return

        raw_msg = self.Peer_connection.receive_message(sock)
        msg = decode_raw_msg(raw_msg)

    # ===== UTILS METHOD FOR INTERESTED =====

    def unchoke_for_interested(self, sock, peer):
        if peer.status.am_choking == False:
            self.send_unchoke(sock, peer)
            return True
        else:
            if len(self.Peer_manager.unchoked_peers) < 2:
                self.Peer_manager.unchoke(sock, peer)
                return True
            else:
                self.Peer_connection.send_choke(sock,peer)
                return False


    # ===== HANDSHAKE =====

    def start_handshake(self):
            with ThreadPoolExecutor(max_workers = 5) as executor:
                futures = [executor.submit(self._handshake, addr) for addr in self.Peer_manager.raw_addrs]
                for future in futures:
                    result = future.result()
            
    def _handshake(self, addr):
        try:
            sock = self.Peer_connection.connect_to_addr(addr)
            handshake_msg = self._build_handshake_msg()
            send_msg(sock, handshake_msg)
            msg = self.Peer_connection.receive_message(sock)
            peer_id = msg.get("peer_id")
            peer_port = msg.get("peer_port")
            new_peer = self._process_peer_handshake(peer_id, addr[0], peer_port)
            
            self._send_bitfield(sock)
            self._receive_and_update_bitfield(sock, new_peer)
        except Exception as e:
            logging.error(f"Unexpected error in _handshake: {e}")
        finally:
            print("Close request hashshake socket")
            sock.close()

    

    # ===== CHOKING LOOP =====
    def start_loop_choking (self):
        choking_thread = threading.Thread(target=self._loop_choking)
        choking_thread.daemon = True
        choking_thread.start()

    def _loop_choking(self):
        while True:
            if self.Piece_manager.pieces_left == 0:
                self.Choke_manager.set_strategy(SeederState())
            self.Choke_manager.run_choking_cycle(self.Peer_manager, self.Peer_connection)
            time.sleep(10) 
    
    # ===== LEECHING =====
    def start_leeching(self):
        leeching_thread = threading.Thread(target = self._leeching)
        leeching_thread.daemon = True
        leeching_thread.start()
    
    def _leeching(self):
        piece_assignments = self.Strategy_manager.select_pieces(self.Piece_manager, self.Peer_manager)
        for peer in piece_assignments:
            send_interested(peer)

    
    # ===== INTERESTED =====
    def send_interested(self, peer):
        sock = self.Peer_connection.connect_to_peer(peer)
        raw_interested_msg = {
            "peer_id": self.id,
            "peer_port": self.port
        }
        interested_msg = encode_intersted(raw_interested_msg)
        send_msg(sock, interested_msg)

# start

    def start(self):
        try:
            self.register()
            self.getlistpeer()
            self.start_listening()
            self.start_handshake()
            self.start_loop_choking()
            self.start_leeching()

            input()
            self.unregister()
        except Exception as e:
            logging.error(f"Start-Client catched error: {e}")
