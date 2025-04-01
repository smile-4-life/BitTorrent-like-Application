import logging
import threading
import socket
import os

from concurrent.futures import ThreadPoolExecutor
from utils.load_config import load_config
from connection.handle_client import HandleClient
from connection.message_protocol import recv_msg, decode_data, encode_data, send_msg

CONFIG_PATH = os.path.join("config", "tracker_config.json")

class TrackerSubject:
    def __init__(self):
        self.peers = {}
        self.data_lock = threading.Lock()
        self.is_running = True

    def running(self):
        input()
        self.is_running = False
        exit()

    def start(self):
        config = load_config(CONFIG_PATH)

        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.bind((config["tracker_IP"], config["tracker_port"]))
        tracker_socket.listen(100)
        logging.info(f"🚀 Tracker running on {config['tracker_IP']}:{config['tracker_port']}")

        threading.Thread(target=self.running).start()

        with ThreadPoolExecutor(max_workers=100) as executor:
            while self.is_running:
                client_sock, addr = tracker_socket.accept()
                executor.submit(self.handle_client, client_sock, addr[0])

    def handle_client(self, client_socket, client_ip):
        handler = HandleClient(self) 
        try:
            biMsg = recv_msg(client_socket)
            if not biMsg:
                logging.warning(f"Client {client_ip} disconnected unexpectedly.")
                return

            dictMsg = decode_data(biMsg)
            logging.info(f"Received message from {client_ip}: {dictMsg}")

            if dictMsg.get("opcode") == "REGISTER":
                handler.handle_register(client_socket,client_ip,dictMsg)
                
        except Exception as e:
            logging.error(f"Error handling client {client_ip}: {e}")
        finally:
            client_socket.close()

    def register_peer(self, peer_addr, list_pieces):
        with self.data_lock:
            if peer_addr not in self.peers:
                self.peers[peer_addr] = list_pieces  #join peer - add new key-values
                print(f"{self.peers[peer_addr]}")
                logging.info(f"✅ Registered peer: {peer_addr}")
                return True
            else:
                logging.info(f"⚠️ Peer already registered: {peer_addr}")
            return False

    def unregister_peer(self, peer_addr):
        with self.data_lock:
            if peer_addr in self.peers:
                del self.peers[peer_addr]   #remove peer
                logging.info(f"✅ Unregister peer: {peer_addr}")
                return True
            logging.warning(f"⚠️ Peer have not registered: {peer_addr}")
            return False
    