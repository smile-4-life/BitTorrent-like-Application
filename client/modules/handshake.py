    
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from protocol.peer_protocol import encode_handshake, encode_bitfield, send_msg, encode_done

class Handshake():
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
            self._select_peers_to_keep()
            
    def _perform_handshake(self, addr):
        try:
            sock = self.Peer_connection.connect_to_addr(addr)
            handshake_msg = self._build_handshake_msg()
            send_msg(sock, handshake_msg)
            logging.info(f"Sent handshake msg to {addr}")
            
            msg = self.Peer_connection.receive_message(sock)
            peer_id = msg.get("peer_id")
            peer_port = msg.get("peer_port")
            new_peer = self._add_peer_after_handshake(sock, peer_id, addr[0], peer_port)


            self._send_bitfield(sock)
            logging.info(f"Sent bitfield msg to {addr}")
            self._receive_and_update_bitfield(sock, new_peer)

            if self.Piece_manager.pieces_left == 0:
                send_msg(sock, encode_done())

        except Exception as e:
            logging.error(f"Unexpected error in _handshake: {e}")

    
    def _select_peers_to_keep(self, max_connection=10):
        peers = self.Peer_manager.get_all_peers()
        sorted_peers = sorted(peers, key=lambda p: p.pieces_left)
        keeping_peers = sorted_peers[:max_connection]
        closing_peers = sorted_peers[max_connection:]
        for peer in closing_peers:
            try:
                self._send_disconnect(peer)
            except Exception as e:
                logging.error(f"Error disconnecting peer {peer.ip}: {e}")

    def _send_disconnect(self, peer):
        try:
            bi_msg = encode_disconnect()
            send_msg(peer.sock, bi_msg)
            peer.sock.close()
        except Exception as e:
            logging.error(f"Error in _send_disconnect: {e}")
        # ===== HANDSHAKE =====


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