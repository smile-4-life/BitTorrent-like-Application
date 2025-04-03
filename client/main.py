import json
import logging
import threading
import sys

from observer.client import ClientObserver

from utils.logger import setup_logger
from utils.metainfo_utils import *
from utils.load_config import load_config

from torrent_manager.create_torrent import choose_upload_file

CONFIG_PATH = "config\\client_config.json"

if __name__ == "__main__":
    setup_logger()
    choose_upload_file()
    client = ClientObserver()
    client.start()
