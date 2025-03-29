import os
import logging

from utils.metainfo_utils import split_file_and_create_torrent, print_torrent_file

def choose_upload_file():
    try:
        file_name = input("Enter file name: ")
        file_path = os.path.join("torrent_factory/file_upload", file_name)

        tracker_IP = input("Enter Tracker IP: ")
        tracker_port = int(input("Enter Tracker port: "))

        tracker_URL = f"{tracker_IP}:{tracker_port}"


        if not os.path.isfile(file_path):
            logging.error(f"Error: File '{file_path}' not found.")
            return
        
        split_file_and_create_torrent(file_path, 512*1024, tracker_URL, "torrent_factory/data/list_pieces")
        print_torrent_file("torrent_factory/metainfo_container/metainfo.torrent")

    except ValueError:
        logging.info("Invalid port number. Please enter a valid integer.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
