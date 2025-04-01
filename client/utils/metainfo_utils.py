import hashlib
import os
import bencodepy
import logging

def split_file_and_create_torrent(upload_file_path, metainfo_file_path, piece_size, tracker_url, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    pieces = []
    hash_list = []

    with open(upload_file_path, 'rb') as file:
        while True:
            piece = file.read(piece_size)
            if not piece:
                break
            pieces.append(piece)

            # Tính toán hash cho từng phần
            piece_hash = hashlib.sha1(piece).hexdigest()
            piece_file_name = f"{piece_hash}.bin"  # Đặt tên file theo hash
            piece_file_path = os.path.join(output_folder, piece_file_name)

            with open(piece_file_path, 'wb') as piece_file:
                piece_file.write(piece)

            hash_list.append(piece_hash) 
            logging.debug(f"{piece_file_path}: Hash = {piece_hash}")
        logging.info(f"Split File into pieces DONE | stored in data/list_pieces")

    #  file torrent
    file_name = os.path.basename(upload_file_path)
    file_size = os.path.getsize(upload_file_path)

    # dictionary lưu hash và đường dẫn
    piece_info = {}
    for i, piece_hash in enumerate(hash_list):
        piece_file_path = os.path.join(output_folder, f"piece_{i}.bin")
        piece_info[piece_hash] = piece_file_path # to bytes

    torrent_info = {
        'announce': tracker_url,
        'info': {
            'name': file_name,
            'piece length': piece_size,
            'pieces': piece_info, #dict hash:count
            'length': file_size
        }
    }

    with open(metainfo_file_path, 'wb') as torrent_file:
        torrent_file.write(bencodepy.encode(torrent_info))
    logging.info(f"Create metainfo file DONE | file_path: '{metainfo_file_path}'")

def read_torrent_file(torrent_file_path):
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
        pieces = info.get(b'pieces')  # list hash       
        file_length = info.get(b'length')
        pieces_count = len(pieces)
        # default bitfield 0 indicate client has not had this piece 
    except Exception as e:
        logging.error(f"Error when dealing with torrent file: {e}")
    return tracker_URL, file_name, piece_length, list_pieces, file_length, pieces_count

def print_torrent_file(torrent_file_path):
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
    logging.info(f"Number of Pieces: {len(pieces)}")  # Số lượng hash tương ứng