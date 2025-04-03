import os
import logging
import json

from utils.metainfo_utils import split_file_and_create_torrent, print_torrent_file

def choose_upload_file():

    config = _load_config()

    pieces_folder = config.get("pieces_folder","torrent_manager\\data\\list_pieces") #output folder

    metainfo_container_folder = config.get("metainfo_container_folder", "metainfo_container")
    metainfo_file_name = config.get("metainfo_file_name", "metainfo.torrent")
    metainfo_file_path = os.path.join(metainfo_container_folder, metainfo_file_name)

    file_upload_container_folder = config.get("file_upload_container_folder", "torrent_manager\\file_upload_container")



    try:
        upload_file_name = input("Enter file name: ")
        upload_file_path = os.path.join(file_upload_container_folder, upload_file_name)

        tracker_IP = input("Enter Tracker IP: ")
        tracker_port = int(input("Enter Tracker port: "))
        tracker_URL = f"{tracker_IP}:{tracker_port}"

        if not os.path.isfile(upload_file_path):
            logging.error(f"Error: File '{upload_file_name}' was not found in folder '{file_upload_container_folder}'.")
            logging.warn(f"Please double check the file name or move the file to the correct folder.")
            return
        
        split_file_and_create_torrent(upload_file_path, metainfo_file_path, tracker_URL, pieces_folder)
        
        print_torrent_file(metainfo_file_path)

    except ValueError:
        logging.info("Invalid port number. Please enter a valid integer.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def _load_config(config_path = "config\\metainfo_config.json"):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"{config_path} could not found!")
            exit()
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON in config file: {config_path}")
            exit()
