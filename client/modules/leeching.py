import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from protocol.peer_protocol import (
    encode_interested,
    encode_request,
    encode_done,
    send_msg
)

class Leeching():
    def __init__(self, id, port, Piece_manager, Peer_manager, Peer_connection, Strategy_manager):
        self.id = id
        self.port = port
        self.Piece_manager = Piece_manager
        self.Peer_manager = Peer_manager
        self.Peer_connection = Peer_connection

        self.Strategy_manager = Strategy_manager
    
    def start_leeching(self):
        leeching_thread = threading.Thread(target = self._leeching)
        leeching_thread.daemon = True
        leeching_thread.start()
    
    def _leeching(self):
        while self.Piece_manager.pieces_left != 0:
            piece_assignments = self.Strategy_manager.select_pieces(self.Piece_manager, self.Peer_manager)
            with ThreadPoolExecutor(max_workers=5) as executor:
                for peer in piece_assignments:
                    executor.submit(self._interact_with_peer,peer,piece_assignments[peer])
            time.sleep(5)
                
    def _interact_with_peer(self, peer, list_pieces):
        try:
            self.send_interested(peer)
            msg = self.Peer_connection.receive_message(peer.sock)
            if msg.get("opcode") == "CHOKED":
                logging.info("Is Choked")
                self.Piece_manager.reset_pieces(list_pieces)
                return
                
            elif msg.get("opcode") == "UNCHOKED":
                self._start_request(peer.sock, list_pieces)
            else:
                logging.info(f"Unexpected msg in interact with peer: {msg}")
        except Exception as e:
            logging.error(f"Unexpected error in _interact_with_peer: {e}")
        finally:
            if peer.sock:
                peer.sock.close()
    
    def _start_request(self, sock, list_pieces):
        try:
            for i, piece in enumerate(list_pieces):
                success = self._request_piece(sock, piece)
                if not success:
                    self.Piece_manager.reset_pieces(list_pieces[i:])
                    return
            bi_msg = encode_done()
            send_msg(sock,bi_msg)
            logging.info(f"Sent DONE")
        except Exception as e:
            logging.error(f"Unexpected error in _start_request: {e}")
    
    def _request_piece(self, sock, piece):
        try:
            msg = {
                "piece_index": piece,
                "peer_id": self.id
            }
            bi_msg = encode_request(msg)
            send_msg(sock,bi_msg)
            logging.info(f"Sent REQUEST")
            response = self.Peer_connection.receive_message(sock)

            if response.get("opcode") == "CHOKED":
                return False

            if response.get("opcode") == "PIECE":
                piece = response.get("piece")
                piece_index = response.get("piece_index")
                self.Piece_manager.down_piece(piece_index, piece)
                return True
        except Exception as e:
            logging.error(f"Unexpected error in _request_piece: {e}")

    # ===== INTERESTED =====
    def send_interested(self, peer):
        raw_interested_msg = {
            "peer_id": self.id,
            "peer_port": self.port
        }
        interested_msg = encode_interested(raw_interested_msg)
        send_msg(peer.sock, interested_msg)
        logging.info(f"Sent interested msg")
