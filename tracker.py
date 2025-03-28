import socket
import threading
import json
import logging

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
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.peers = {}  # storage

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind((self.host, self.port))
            logging.info(f"📡 Tracker running on {self.host}:{self.port}")
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
