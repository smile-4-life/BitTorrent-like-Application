import sys
import os
import json
import logging

# Add the parent directory to the path to resolve the shared module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.config_loader import load_config
from utils.logging_config import setup_logging
from torrent_factory.create_torrent import choose_upload_file
from observer.client import *

CONFIG_PATH = "config/client_config.json"
config = load_config(CONFIG_PATH)

def main():
    setup_logging()
    
    if len(sys.argv) > 1 and sys.argv[1] == "register-seed":
        logging.info("[Start seeding your file]")
        choose_upload_file()

    else:
        client = TorrentClient()

    #connect_tracker()

if __name__ == "__main__":
    main()
