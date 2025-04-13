import threading
import hashlib
import os
import logging

from manager.piece_lock_manager import Lock_manager
from utils.torrent_reader import TorrentReader

class PieceManager:
    def __init__(self, config):
        self.bitfield_lock = threading.Lock()

        self.download_folder_path = config['download_folder_path']
        self.metainfo_file_path = config['metainfo_file_path']

        Reader = TorrentReader()
        (
            self.tracker_URL,
            self.file_name,
            self.piece_length,
            self.list_pieces,
            self.file_length,
            self.pieces_count
        ) = Reader.read_torrent_file(self.metainfo_file_path)
        self.pieces_left = self.pieces_count
        self.downloaded_count = 0

        self.hash_to_index = {h.decode('utf-8'): i for i, h in enumerate(self.list_pieces)}
        self.index_to_hash = {i: h.decode('utf-8') for i, h in enumerate(self.list_pieces)}
        self.index_bitfield = {i: 0 for i in range(len(self.list_pieces))}

        self.scan_downloaded_pieces()

    def scan_downloaded_pieces(self):
        os.makedirs(self.download_folder_path, exist_ok=True)
        existing_pieces = os.listdir(self.download_folder_path)
        for file in existing_pieces:
            if file.endswith('.bin'):
                piece_hash = file[:-4]
                if piece_hash in self.hash_to_index.keys():
                    index = self.hash_to_index[piece_hash]
                    self.index_bitfield[index] = 1
                    self.pieces_left -= 1
                    self.downloaded_count += 1

    # bitfield

    def get_list_bitfield(self):
        with self.bitfield_lock:
            return [bitfield for index, bitfield in self.index_bitfield.items()]
    
    def get_str_bitfield(self):
        with self.bitfield_lock:
            return ''.join('1' if bitfield == 1 else '0' for index, bitfield in self.index_bitfield.items())

    # needed pieces 

    def get_missing_pieces(self):
        with self.bitfield_lock:
            return [index for index, bitfield in self.index_bitfield.items() if bitfield == 0]
    
    # set bitfield 0 - 1 - 2

    def set_downloading_piece(self, index):
        with self.bitfield_lock:
            self.index_bitfield[index] = 2
    
    def set_downloading_pieces(self, list_index):
        with self.bitfield_lock:
            for index in list_index:
                self.index_bitfield[index] = 2
    
    def reset_piece(self, index):
        with self.bitfield_lock:
            if self.index_bitfield.get(index) == 2:
                self.index_bitfield[index] = 0

    def reset_pieces(self, list_index):
        with self.bitfield_lock:
            for index in list_index:
                if self.index_bitfield.get(index) == 2:
                    self.index_bitfield[index] = 0
    
    # load piece to upload

    def load_piece(self,piece_index):
        try:
            piece_file = os.path.join(    self.download_folder_path, 
                                          f"{self.index_to_hash[piece_index]}.bin")
            lock = Lock_manager.get_lock(piece_index)
            with lock:
                with open(piece_file, 'rb') as f:
                    piece = f.read()
                    return piece
        except FileNotFoundError:
            logging.error(f"Error: file for piece {piece_index} not found at {piece_file}")
            return None
    
    def down_piece(self, piece_index, piece):
        try:
            piece_file = os.path.join(    self.download_folder_path, 
                                          f"{self.index_to_hash[piece_index]}.bin")
            lock = Lock_manager.get_lock(piece_index)
            with lock:
                with open(piece_file, 'wb') as f:
                    f.write(piece)
            
            hash_value = hashlib.sha1(piece).hexdigest()
            expected_hash = self.index_to_hash[piece_index]

            if hash_value != expected_hash:
                logging.warning(f"Hash mismatch for piece {piece_index}. Expected {expected_hash}, got {hash_value}")
                os.remove(piece_file)
                return False

            self.pieces_left-=1
            self.downloaded_count+=1
            return True
        except FileNotFoundError:
            logging.error(f"Error: file for piece {piece_index} not found at {piece_file}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error in down_piece: {e}")
        return False