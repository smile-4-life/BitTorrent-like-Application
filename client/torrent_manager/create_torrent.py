import os
import logging
import json
import hashlib
import bencodepy

class TorrentManager:
    def __init__(self, config_path="config/metainfo_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.pieces_folder = self.config.get("pieces_folder", "torrent_manager\\data\\list_pieces")
        self.metainfo_container_folder = self.config.get("metainfo_container_folder", "metainfo_container")
        self.metainfo_file_name = self.config.get("metainfo_file_name", "metainfo.torrent")
        self.metainfo_file_path = os.path.join(self.metainfo_container_folder, self.metainfo_file_name)
        self.file_upload_container_folder = self.config.get("file_upload_container_folder", "torrent_manager\\file_upload_container")

    def choose_upload_file(self):
        try:
            upload_file_name = input("Enter file name: ")
            upload_file_path = os.path.join(self.file_upload_container_folder, upload_file_name)

            tracker_ip = input("Enter Tracker IP: ")
            tracker_port = int(input("Enter Tracker port: "))
            tracker_url = f"{tracker_ip}:{tracker_port}"

            if not os.path.isfile(upload_file_path):
                logging.error(f"Error: File '{upload_file_name}' was not found in folder '{self.file_upload_container_folder}'.")
                logging.warning("Please double-check the file name or move the file to the correct folder.")
                return
            
            self._split_file_and_create_torrent(upload_file_path, self.metainfo_file_path, tracker_url, self.pieces_folder)
            
            self.print_torrent_file(self.metainfo_file_path)

        except ValueError:
            logging.info("Invalid port number. Please enter a valid integer.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
    
    def print_torrent_file(self, torrent_file_path):
        with open(torrent_file_path, 'rb') as torrent_file:
            torrent_data = bencodepy.decode(torrent_file.read())

        info = torrent_data[b'info']
        file_name = info[b'name'].decode()
        file_size = info[b'length']
        piece_length = info[b'piece length']
        pieces = info[b'pieces']

        logging.info(f"File Name: {file_name}")
        logging.info(f"File Size: {file_size} bytes")
        logging.info(f"Piece Length: {piece_length} bytes")
        logging.info(f"Number of Pieces: {len(pieces)}")

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"{self.config_path} could not be found!")
            exit()
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON in config file: {self.config_path}")
            exit()

    def _estimate_piece_size(self, file_size):
        MB = 1024 * 1024
        file_size_mb = file_size / MB

        if file_size_mb <= 100:
            return 64 * 1024  # 64 KB
        elif file_size_mb <= 1024:
            return 256 * 1024  # 256 KB
        elif file_size_mb <= 4096:
            return 512 * 1024  # 512 KB
        elif file_size_mb < 10240:
            return 1024 * 1024  # 1 MB
        elif file_size_mb < 50000:
            return 2 * MB  # 2 MB
        else:
            return 4 * MB  # 4 MB

    def _split_file_and_create_torrent(self, upload_file_path, metainfo_file_path, tracker_url, output_folder):
        os.makedirs(output_folder, exist_ok=True)

        pieces = []
        hash_list = []

        file_name = os.path.basename(upload_file_path)
        file_size = os.path.getsize(upload_file_path)
        piece_size = self._estimate_piece_size(file_size)

        with open(upload_file_path, 'rb') as file:
            while True:
                piece = file.read(piece_size)
                if not piece:
                    break
                pieces.append(piece)

                piece_hash = hashlib.sha1(piece).hexdigest()
                piece_file_name = f"{piece_hash}.bin"
                piece_file_path = os.path.join(output_folder, piece_file_name)

                with open(piece_file_path, 'wb') as piece_file:
                    piece_file.write(piece)

                hash_list.append(piece_hash) 
                logging.debug(f"{piece_file_path}: Hash = {piece_hash}")
            logging.info(f"Split File into pieces DONE | stored in data/list_pieces")

        piece_info = {piece_hash: os.path.join(output_folder, f"piece_{i}.bin") for i, piece_hash in enumerate(hash_list)}

        torrent_info = {
            'announce': tracker_url,
            'info': {
                'name': file_name,
                'piece length': piece_size,
                'pieces': piece_info,
                'length': file_size
            }
        }

        with open(metainfo_file_path, 'wb') as torrent_file:
            torrent_file.write(bencodepy.encode(torrent_info))
        logging.info(f"Create metainfo file DONE | file_path: '{metainfo_file_path}'")

