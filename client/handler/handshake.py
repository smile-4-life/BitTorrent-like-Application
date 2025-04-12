    
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from protocol.peer_protocol import encode_handshake, encode_bitfield, send_msg

class Handshake:
    def __init__(self, id, port, Piece_manager, Peer_manager, Peer_connection, Peer_factory):
        self.id = id
        self.port = port
        self.Piece_manager = Piece_manager
        self.Peer_manager = Peer_manager
        self.Peer_connection = Peer_connection
        
        self.Peer_factory = Peer_factory
        
    def start_handshake(self):
            with ThreadPoolExecutor(max_workers = 5) as executor:
                futures = [executor.submit(self._perform_handshake, addr) for addr in self.Peer_manager.raw_addrs]
                for future in futures:
                    result = future.result()
            
    def _perform_handshake(self, addr):
        try:
            sock = self.Peer_connection.connect_to_addr(addr)
            handshake_msg = self._build_handshake_msg()
            send_msg(sock, handshake_msg)
            
            msg = self.Peer_connection.receive_message(sock)
            peer_id = msg.get("peer_id")
            peer_port = msg.get("peer_port")
            new_peer = self._add_peer_after_handshake(peer_id, addr[0], peer_port)

            logging.info(f"Sent handshake msg to {addr}")

            self._send_bitfield(sock)
            self._receive_and_update_bitfield(sock, new_peer)
        except Exception as e:
            logging.error(f"Unexpected error in _handshake: {e}")
        finally:
            logging.info("Close request hashshake socket")
            sock.close()
    
        # ===== HANDSHAKE =====

    def handle_handshake(self, sock, peer_ip, msg):
        try:
            peer_id = msg.get("peer_id")
            peer_port = msg.get("peer_port")
            new_peer = self._add_peer_after_handshake(peer_id, peer_ip, peer_port)
            
            reply_msg = self._build_handshake_msg()
            send_msg(sock, reply_msg)
            
            self._receive_and_update_bitfield(sock, new_peer)
            self._send_bitfield(sock)
        except Exception as e:
            logging.error(f"Unexpected error in handle_handshake: {e}")
        finally:
            logging.info("Close handshake socket")
            sock.close()

    def _add_peer_after_handshake(self, peer_id, peer_ip, peer_port):
        addr = (peer_ip, peer_port)
        self.Peer_manager.remove_raw_addr(addr)
        new_peer = self.Peer_factory.new_peer(peer_id, addr)
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
            "str_bitfield": self.Piece_manager.get_str_bitfield()
        }
        bi_msg = encode_bitfield(msg)
        send_msg(sock, bi_msg)

    def _receive_and_update_bitfield(self, sock, peer):
        msg = self.Peer_connection.receive_message(sock)
        list_bitfield = msg.get("str_bitfield")
        self.Peer_manager.update_index_bitfield(peer, list_bitfield)