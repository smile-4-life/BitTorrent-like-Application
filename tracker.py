import socket
import threading
import json
import logging
import os

logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt='%H:%M:%S',
        handlers=[
            #logging.FileHandler("client.log"), 
            logging.StreamHandler()  
        ]
    )

class TorrentTracker:
    def __init__(self, ):
        self.load_config()
        self.peers = {}  # storage
    
    def load_config(self, config_path = 'config/trackerConfig.json'):
        if not os.path.exists(config_path):
            logging.error(f"❌ Config file '{config_path}' not found.")
            exit(1)

        with open(config_path, 'r') as f:
            config = json.load(f)

        self.IP = config.get('tracker_ip','127.0.0.1')
        self.port = config.get('tracker_port',8080)

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind((self.IP, self.port))
            logging.info(f"📡 Tracker running on {self.IP}:{self.port}")
        except Exception as e:
            logging.error(f"❌This tracker is unable to bind the port: {e}")
        server.listen(5)

        while True:
            client_socket, addr = server.accept()
            logging.info(f"🔗 Connection from: {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()


    def handle_client(self, sock):
        logging.info(f"Handle client")


if __name__ == "__main__":
    tracker = TorrentTracker()
    tracker.start()
