import socket
import threading
import logging
import os
import json

from concurrent.futures import ThreadPoolExecutor
from utils.logger import setup_logger
from subject.tracker import TrackerSubject
from connection.tracker_handler import HandleClient

def handle_client(client_socket, addr, client_tracker):
    try:
        request = client_socket.recv(1024).decode()
        if not request:
            return

        command, *args = request.split()

        if command == "REGISTER":
            logging.info("🔗 Received: REGISTER")
            client_tracker.handle_register(addr[0], int(args[1]), client_socket)

        elif command == "UPDATE_PIECE":
            client_tracker.handle_update_piece(addr[0], int(args[1]), args[2])

        elif command == "GET_PEERS_DICT":
            logging.info("🔗 Received: GET_PEERS_DICT")
            client_tracker.handle_get_list_peer(client_socket)

        elif command == "UNREGISTER":
            logging.info("🔗 Received: UNREGISTER")
            client_tracker.handle_unregister(addr[0], int(args[1]), client_socket)
        
        else:
            logging.warning(f"❌ Unexpected request from {addr}: {request}")

    except Exception as e:
        logging.error(f"⚠️ Error handling client {addr}: {e}")

    finally:
        client_socket.close()

def start_tracker():
    """Starts the tracker server."""
    config = load_config()
    tracker_ = TrackerSubject()
    client_tracker = HandleClient(tracker_)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((config["tracker_IP"], config["tracker_port"]))
    server.listen(100)
    logging.info(f"🚀 Tracker running on {config['tracker_IP']}:{config['tracker_port']}")

    with ThreadPoolExecutor(max_workers=100) as executor:
        while True:
            client_sock, addr = server.accept()
            executor.submit(handle_client, client_sock, addr, client_tracker)

def load_config(config_path="config/tracker_config.json"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"❌ Config file '{config_path}' not found.")

    with open(config_path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    setup_logger()
    start_tracker()
