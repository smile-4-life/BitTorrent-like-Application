import threading
import hashlib

from manager.piece_lock_manager import lock_manager
from utils.torrent_reader import TorrentReader

class PieceManager:
    def __init__(self, config):
        self.bitfield_lock = threading.Lock()

        self.download_folder_path = config['download_folder_path']
        self.scan_downloaded_pieces()

        self.metainfo_file_path = config['metainfo_file_path']

        Reader = TorrentReader()
        (
            self.tracker_URL,
            self.file_name,
            self.piece_length,
            self.list_pieces,
            self.file_length,
            self.pieces_left
        ) = Reader.read_torrent_file(self.metainfo_file_path)

        self.hash_to_index = {h: i for i, h in enumerate(self.list_pieces)}
        self.index_to_hash = {i: h for i, h in enumerate(self.list_pieces)}

        self.piece_bitfield = {i: 0 for i in range(len(self.list_pieces))}

    def scan_downloaded_pieces(self):
        import os
        existing_pieces = os.listdir(self.download_folder_path)
        for file in existing_pieces:
            if file.endswith('.bin'):
                piece_hash = file[:-4]
                if piece_hash in self.hash_to_index:
                    index = self.hash_to_index[piece_hash]
                    self.piece_bitfield[index] = 1
                    self.pieces_left -= 1

    def has_piece(self, piece_index):
        with self.bitfield_lock:
            return self.piece_bitfield.get(piece_index, 0) == 1

    def verify_piece(self, piece_index, data):
        expected_hash = self.index_to_hash[piece_index]
        actual_hash = hashlib.sha1(data).hexdigest()
        return actual_hash == expected_hash

    def verify_and_save(self, piece_index, data):
        expected_hash = self.index_to_hash[piece_index]
        actual_hash = hashlib.sha1(data).hexdigest()
        if actual_hash == expected_hash:
            lock = lock_manager.getlock(piece_hash)
            piece_path = os.path.join(self.download_folder_path, f"{self.index_to_hash[piece_index]}.bin")
            with lock:
                with open(piece_path, 'wb') as f:
                    f.write(data)
            with self.bitfield_lock:
                self.piece_bitfield[piece_index] = 1
                self.pieces_left -= 1
        else:
            logging.warnning(f"Expected {actual_hash} but receive {expected_hash} - did no reveive piece {piece_index}.")

    def get_missing_pieces(self):
        with self.bitfield_lock:
            return [i for i, have in self.piece_bitfield.items() if have == 0]

    def get_bitfield(self):
        with self.bitfield_lock:
            return dict(self.piece_bitfield)

    def get_pieces_left(self):
        with self.bitfield_lock:
            return self.pieces_left
