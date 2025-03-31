import json
import logging
import threading

from utils.logger import setup_logger
from observer.client import ClientObserver
from utils.metainfo_utils import read_torrent_file



if __name__ == "__main__":
    setup_logger()

    client_ip = "0.0.0.0"

    client = ClientObserver()

    client.start()
