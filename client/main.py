import json
import logging
import threading
from observer.client import ClientObserver
from utils.metainfo_utils import read_torrent_file


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler()]
)

if __name__ == "__main__":
    client_ip = "0.0.0.0"

    client = ClientObserver()

    this_addr = client.register_peer()
    if this_addr is None:
        exit()

    client_ip = this_addr.split(":")[0]
    
    threading.Thread(target=client.unregister, daemon=True).start()
    
    input("Enter to quit.")
