import json
import logging
import threading
from observer.client import ClientObserver
from utils.metainfo_utils import read_torrent_file

# Load configuration
with open("config/client_config.json", 'r') as f:
    config = json.load(f)

METAINFO_FILE_PATH = config["metainfo_file_path"]
CLIENT_PORT = config["client_port"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler()]
)

if __name__ == "__main__":
    client_ip = "0.0.0.0"
    
    hash_dict, tracker_url, file_name, piece_length, pieces, file_length, pieces_count = read_torrent_file(METAINFO_FILE_PATH)

    client = ClientObserver(client_ip, CLIENT_PORT, tracker_url)
    client.hash_dict = hash_dict

    this_addr = client.register_peer()
    if this_addr is None:
        exit()

    client_ip = this_addr.split(":")[0]
    
    threading.Thread(target=client.unregister, daemon=True).start()
    
    input("Enter to quit.")
