import logging
import threading
import socket
import os

from concurrent.futures import ThreadPoolExecutor

from utils.load_config import load_config
from connection.handle_client import HandleClient
from protocol.tracker_protocol import recv_msg, decode_data, encode_data, send_msg

CONFIG_PATH = os.path.join("config", "tracker_config.json")

class Tracker:
    def __init__(self):

        self.peers = []      #list of Peer Object
        self.peers_lock = threading.Lock()

        self.is_running = True

    def running(self):
        input()
        self.is_running = False
        exit()

    def start(self):
        threading.Thread(target=self.run_server, daemon=True).start()
        input()

    def run_server(self):
        config = load_config(CONFIG_PATH)

        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.bind((config["tracker_IP"], config["tracker_port"]))
        tracker_socket.listen(100)
        logging.info(f"🚀 Tracker running on {config['tracker_IP']}:{config['tracker_port']}")


        with ThreadPoolExecutor(max_workers=100) as executor:
            while self.is_running:
                client_sock, addr = tracker_socket.accept()
                executor.submit(self.handle_client, client_sock, addr[0])

    def handle_client(self, client_socket, client_ip):
        handler = HandleClient()
        
        try:
            #check msge
            biMsg = recv_msg(client_socket)
            if not biMsg:
                logging.warning(f"Client {client_ip} disconnected unexpectedly.")
                return
            
            dictMsg = decode_data(biMsg)
            if not dictMsg:
                logging.warning(f"Received invalid data from {client_ip}.")
                return

            logging.info(f"Received message from {client_ip}: {dictMsg}")

            opcode = dictMsg.get("opcode")
            if not opcode:
                logging.warning(f"Missing opcode in message from {client_ip}.")
                return

            #handle by opcode
            if opcode == "REGISTER":
                self.handle_register_logic(client_socket, client_ip, dictMsg)
            elif opcode == "GETPEER":
                self.handle_get_peer_logic(client_socket)
            elif opcode == "UNREGISTER":
                self.handle_unregister_logic(client_socket, client_ip, dictMsg)
            else:
                logging.warning(f"Unknown opcode '{opcode}' from {client_ip}.")

        except Exception as e:
            logging.error(f"Error handling client {client_ip}: {e}")
        finally:
            client_socket.close()

    def handle_register_logic(self, client_socket, client_ip, dictMsg):      #add new observer to data
        handler = HandleClient()
        new_peer = handler.handle_register(client_socket, client_ip, dictMsg)
        
        if new_peer not in self.peers:
            self.peers.append(new_peer) 
            logging.info(f"Added new peer: {new_peer.ip}:{new_peer.port}")
        else:
            logging.info(f"Peer {new_peer.ip}:{new_peer.port} is already registered.")

    def handle_get_peer_logic(self, client_socket):                        #no update data, just give data to observer
        handler = HandleClient()
        handler.handle_get_peers(client_socket, self.peers)
    
    def handle_unregister_logic(self, client_socket, client_ip, dictMsg):      # remove observer from data
        handler = HandleClient()
        this_peer = handler.handle_unregister(client_socket, client_ip, dictMsg)
        
        if this_peer in self.peers:
            self.peers.remove(this_peer) 
            logging.info(f"Removed peer: {this_peer.ip}:{this_peer.port}")
        else:
            logging.info(f"Peer {this_peer.ip}:{this_peer.port} is not found.")
    

