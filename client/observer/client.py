import socket
import logging
import threading
import json
import os

class TorrentClient:
    def __init__(self, config_path="config/client_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.tracker_host = self.config.get("tracker_host")
        self.tracker_port = self.config.get("tracker_port")
        self.download_dir = self.config.get("download_dir")
        self.piece_size = self.config.get("piece_size")
        self.algorithm = self.config.get("algorithm")
        self.max_connections = self.config.get("max_connections")

        os.makedirs(self.download_dir, exist_ok=True)
        logging.info(f"Download directory set to: {self.download_dir}")

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file not found at: {self.config_path}")
            exit()
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON in config file: {self.config_path}")
            exit()

    def register_with_tracker(self):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.tracker_host, self.tracker_port))
            logging.info(f"✅ Connected to tracker at {self.tracker_host}:{self.tracker_port}.")

            threading.Thread(target=self.listen_for_updates, args=(client_socket,)).start()

            while True:
                message = input("Enter message to tracker: ")
                client_socket.sendall(message.encode())
        except ConnectionRefusedError:
            logging.error(f"❌ Connection to tracker at {self.tracker_host}:{self.tracker_port} refused. Ensure the tracker is running.")
        except Exception as e:
            logging.error(f"Error connecting to tracker: {e}")

    def listen_for_updates(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if data:
                    logging.info(f"📬 Update from tracker: {data}")
                else:
                    logging.info("Connection to tracker closed.")
                    break
        except ConnectionResetError:
            logging.error("❌ Connection to tracker was reset by the server.")
        except Exception as e:
            logging.error(f"Error receiving updates: {e}")
        finally:
            client_socket.close()
