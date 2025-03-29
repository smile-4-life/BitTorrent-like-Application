import sys
import os
import json

# Add the parent directory to the path to resolve the shared module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.socket_handler import connect_to_tracker
from metainfo.torrent_creator import *
from shared.config_loader import load_config

CONFIG_PATH = "config/client_config.json"
config = load_config(CONFIG_PATH)

def main():
    print("[Client] Starting...")
    split_file_and_create_torrent(FILE_PATH, PIECE_SIZE, TRACKER_URL, 'list_pieces')
    print_torrent_file(TORRENT_FILE_PATH)
    

if __name__ == "__main__":
    main()
