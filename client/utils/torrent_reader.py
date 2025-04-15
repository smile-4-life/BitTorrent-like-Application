import os
import bencodepy
import logging
import hashlib

class TorrentReader:
    def read_torrent_file(self,torrent_file_path):
        try:
            if not os.path.exists(torrent_file_path):
                logging.error(f"File {torrent_file_path} not found.")
                exit()

            with open(torrent_file_path, 'rb') as torrent_file:
                torrent_data = bencodepy.decode(torrent_file.read())

            tracker_URL = torrent_data.get(b'announce', b'').decode()  # x.x.x.x:y
            info = torrent_data.get(b'info')
            file_name = info.get(b'name')
            piece_length = info.get(b'piece length', 0)  # 512KB
            list_pieces = info.get(b'pieces')  # list hash       
            file_length = info.get(b'length')
            pieces_count = len(list_pieces)
            # default bitfield 0 indicate client has not had this piece 
            info_hash = hashlib.sha1(bencodepy.encode(info)).digest()
        except Exception as e:
            logging.error(f"Error when dealing with torrent file: {e}")
        return tracker_URL, file_name, piece_length, list_pieces, file_length, pieces_count, info_hash