import json
import logging
import threading
import sys

from observer.client import ClientObserver
from utils.logger import setup_logger
from torrent_manager.create_torrent import TorrentManager

if __name__ == "__main__":
    setup_logger()

    torrent_manager = TorrentManager()
    torrent_manager.choose_upload_file()

    client = ClientObserver()
    client.start()
