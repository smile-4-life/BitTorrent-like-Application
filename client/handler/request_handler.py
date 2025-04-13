import threading
import time
import logging

from protocol.peer_protocol import *

class HandleRequest():
    def __init__(self, id, port, Piece_manager, Peer_manager, Peer_connection):
        self.id = id
        self.port = port
        self.Piece_manager = Piece_manager
        self.Peer_manager = Peer_manager
        self.Peer_connection = Peer_connection


    def handle_request(self, sock, peer_ip, msg):
        if msg.get("opcode") == "REQUEST":
            peer_id = msg.get("peer_id")
            peer = self.Peer_manager.get_peer(peer_id)
            if peer:
                if peer.status.am_choking == True:
                    self.Peer_manager.send_choked(sock, peer)
                    logging.info(f"Choke peer {peer_id} while being requested")
                    return
            else:
                logging.error(f"Cant found peer {peer_id}")
                return
            piece_index = msg.get("piece_index")
            piece = self.Piece_manager.load_piece(piece_index)
            raw_msg = {
                "opcode": "PIECE",
                "piece": piece,
                "piece_index": piece_index
            }
            bi_msg = encode_piece(raw_msg)
            send_msg(sock, bi_msg)
            logging.debug(f"Sent piece to {peer.ip}:{peer.port}")
        
        elif msg.get("opcode") == "DONE":
            sock.close()
            return
        
        else:
            logging.warning(f"Unexpected Opcode: {msg}")
            return