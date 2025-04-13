    
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from protocol.peer_protocol import encode_handshake, encode_bitfield, send_msg

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
            new_peer = self._add_peer_after_handshake(sock, peer_id, peer_ip, peer_port)
            
            reply_msg = self._build_handshake_msg()
            send_msg(sock, reply_msg)
            
            self._receive_and_update_bitfield(sock, new_peer)
            self._send_bitfield(sock)
        except Exception as e:
            logging.error(f"Unexpected error in handle_handshake: {e}")

    def _add_peer_after_handshake(self, sock, peer_id, peer_ip, peer_port):
        addr = (peer_ip, peer_port)
        self.Peer_manager.remove_raw_addr(addr)
        new_peer = self.Peer_factory.new_peer(sock, peer_id, addr)
        self.Peer_manager.add_active_peer(new_peer)
        return new_peer

    def _build_handshake_msg(self):
        return encode_handshake(
            {
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
        msg = self.Peer_connection.receive_message(sock)
        pieces_left = msg.get("pieces_left")
        list_bitfield = msg.get("str_bitfield")
        self.Peer_manager.update_index_bitfield(peer, pieces_left, list_bitfield)