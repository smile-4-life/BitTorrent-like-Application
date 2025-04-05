import socket
import logging
import struct
import time
from protocol.peer_protocol import *  # Import peer-related protocol methods

class HandlePeer:
    def __init__(self):
        pass

    def connect_to_peer(self, peer_ip, peer_port):
        for attempt in range(1, 4):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((peer_ip, peer_port))
                return sock
            except Exception as e:
                logging.warning(f"⚠️ Attempt {attempt}: Cannot connect to peer ({peer_ip}:{peer_port}) - {e}")
                time.sleep(1)
        logging.error(f"❌ Failed to connect to peer {peer_ip}:{peer_port} after 3 attempts.")
        raise ConnectionError(f"Unable to connect to peer {peer_ip}:{peer_port}")

    def send_request(self, sock, piece_hash):
        try:
            request_msg = encode_request(piece_index)
            send_msg(sock, request_msg)
            logging.info(f"Sent request for piece {piece_index}")
        except Exception as e:
            logging.error(f"Error sending request to peer: {e}")
            raise

    def receive_piece(self, sock):
        try:
            raw_response = recv_msg(sock)
            response = decode_piece(raw_response)
            logging.info(f"Received piece {response['piece_index']}")
            return response
        except Exception as e:
            logging.error(f"Error receiving piece from peer: {e}")
            raise

    def send_have(self, sock, piece_index):
        try:
            have_msg = encode_have(piece_index)
            send_msg(sock, have_msg)
            logging.info(f"Sent HAVE message for piece {piece_index}")
        except Exception as e:
            logging.error(f"Error sending HAVE message to peer: {e}")
            raise

    def listen_for_requests(self, sock):
        try:
            while True:
                raw_request = recv_msg(sock)
                request = decode_peer_message(raw_request)
                if request['opcode'] == 'REQUEST':
                    piece_index = request['piece_index']
                    logging.info(f"Received REQUEST for piece {piece_index}")
                    # You can implement the logic to send the piece back here
                    self.send_piece(sock, piece_index)
                elif request['opcode'] == 'HAVE':
                    piece_index = request['piece_index']
                    logging.info(f"Received HAVE message for piece {piece_index}")
                    # Handle peer's HAVE message here (e.g., track which pieces the peer has)
        except Exception as e:
            logging.error(f"Error during listen_for_requests: {e}")
            raise

    def send_piece(self, sock, piece_index):
        try:
            # This should load the piece's data from storage or memory
            piece_data = self.get_piece_data(piece_index)
            piece_msg = encode_piece(piece_index, piece_data)
            send_msg(sock, piece_msg)
            logging.info(f"Sent piece {piece_index}")
        except Exception as e:
            logging.error(f"Error sending piece to peer: {e}")
            raise

    def get_piece_data(self, piece_hash, download_folder_path):
        download_file_path = os.path.join(download_folder_path,"list_pieces", f"{piece_hash}.bin") + 
        with open(download_file_path, 'wb') as f:
                    f.write(file_data)

    def close_connection(self, sock):
        """Close the connection to the peer."""
        try:
            sock.close()
            logging.info("Closed connection to peer.")
        except Exception as e:
            logging.error(f"Error closing connection: {e}")
            raise
