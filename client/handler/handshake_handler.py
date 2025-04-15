    
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from utils.error import HandleError

from protocol.peer_protocol import encode_handshake, encode_bitfield, encode_done, send_msg

class HandleHandshake():
    def __init__(self, id, port, Piece_manager, Peer_manager, Peer_connection, Peer_factory):
        self.id = id
        self.port = port
        self.Piece_manager = Piece_manager
        self.Peer_manager = Peer_manager
        self.Peer_connection = Peer_connection

        self.Peer_factory = Peer_factory
        

    def handle_handshake(self, sock, peer_ip, msg):
        try:   
            peer_id = msg.get("peer_id")
            peer_port = msg.get("peer_port")

            if not msg.get("info_hash") == self.Piece_manager.info_hash:
                raise HandleError(f"Handshake failed: info_hash does not match for {peer_id}") 
            new_peer = self._add_peer_after_handshake(sock, peer_id, peer_ip, peer_port)
            
            reply_msg = self._build_handshake_msg()
            send_msg(sock, reply_msg)
            
            self._receive_and_update_bitfield(sock, new_peer)
            self._send_bitfield(sock)
        except HandleError:
            raise
        except OSError:
            raise
        except Exception as e:
            logging.error(f"Unexpected error in handle_handshake: {e}")
            raise

    def _add_peer_after_handshake(self, sock, peer_id, peer_ip, peer_port):
        
        if self.Peer_manager.get_peer(peer_id) is not None:
            raise HandleError(f"Handshake failed: Duplicate Peer {peer_id}.")

        addr = (peer_ip, peer_port)
        self.Peer_manager.remove_raw_addr(addr)
        new_peer = self.Peer_factory.new_peer(sock, peer_id, addr)
        self.Peer_manager.add_active_peer(new_peer)
        return new_peer

    def _build_handshake_msg(self):
        return encode_handshake(
            {
                "info_hash": self.Piece_manager.info_hash,
                "peer_id": self.id,
                "peer_port": self.port
            }
        )

    def _send_bitfield(self, sock):
        msg = {
            "pieces_left": self.Piece_manager.pieces_left,
            "str_bitfield": self.Piece_manager.get_str_bitfield()
        }
        bi_msg = encode_bitfield(msg)
        send_msg(sock, bi_msg)

    def _receive_and_update_bitfield(self, sock, peer):
        try:
            msg = self.Peer_connection.receive_message(sock)
            pieces_left = msg.get("pieces_left")
            list_bitfield = msg.get("str_bitfield")
            self.Peer_manager.update_index_bitfield(peer, pieces_left, list_bitfield)
        except OSError:
            raise
        except Exception as e:
            logging.error(f"Unexpected error in _receive_and_update_bitfield: {e}")