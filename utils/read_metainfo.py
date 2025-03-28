import os
import logging
import time
import bencodepy

def read_torrent_file(torrent_file_path):
    hash_dict, tracker_URL, file_name, piece_length, pieces, file_length, pieces_count = {}, '', '', 0, [], 0, 0
    try:
        if not os.path.exists(torrent_file_path):
            print(f"File {torrent_file_path} not found.")
            sys.exit()

        start_time = time.time()
        try:
            with open(torrent_file_path, 'rb') as torrent_file:
                torrent_data = bencodepy.decode(torrent_file.read())
        except IOError:
            if time.time() - start_time > 3:
                raise TimeoutError(f"File {torrent_file_path} is still in use after {3} seconds.")
        tracker_URL = torrent_data.get(b'announce', b'').decode()  # x.x.x.x:y
        info = torrent_data.get(b'info')
        file_name = info.get(b'name')
        piece_length = info.get(b'piece length', 0)  # 512KB
        pieces = info.get(b'pieces')  # list hash       
        file_length = info.get(b'length')
        pieces_count = len(pieces)
        # default bitfield 0 indicate client has not had this piece 
        hash_dict = {piece_hash.decode(): 0 for piece_hash in pieces.keys()} 
    except Exception as e:
        logging.error(f"Error when dealing with torrent file: {e}")
    return hash_dict, tracker_URL, file_name, piece_length, pieces, file_length, pieces_count  