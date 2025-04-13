import threading
import logging
from protocol.peer_protocol import *


class PeerManager:
    def __init__(self, id):
        self.id = id
        self.index_bitfield_lock = threading.Lock()

        self.raw_addrs_lock = threading.Lock()
        self.active_addrs_lock = threading.Lock()
        self.active_peers_lock = threading.Lock()
        self.inflight_request_lock = threading.Lock()
        self.unchoked_peers_lock = threading.Lock()

        self.raw_addrs = []     # [list of tuple (ip,port)]
        self.active_addrs = []
        self.active_peers = []  # [list of object]
        self.inflight_request = [] # list requesting peers
        self.unchoked_peers = [] #list unchoked peers


    # raw

    def add_raw_addr(self, addr):
        with self.raw_addrs_lock:
            if addr not in self.raw_addrs and addr not in self.active_addrs:
                self.raw_addrs.append(addr)
    
    def remove_raw_addr(self, addr):
        with self.raw_addrs_lock:
            if addr in self.raw_addrs:
                self.raw_addrs.remove(addr)
                with self.active_addrs_lock:
                    self.active_addrs.append(addr)
            

    # active

    def add_active_peer(self, peer):
        with self.active_peers_lock:
            if peer not in self.active_peers:
                self.active_peers.append(peer)

    # inflight

    def add_inflight_request(self, peer):
        with self.inflight_request_lock:
            if peer not in self.inflight_request:
                inflight_request.append(peer)
    
    def remove_inflight_request(self, peer):
        with self.inflight_request_lock:
            if peer in self.inflight_request:
                self.inflight_request.remove(peer)

    # unchoked peers

    def add_unchoked_peer(self, peer):
        with self.unchoked_peers_lock:
            if peer not in self.unchoked_peers:
                self.unchoked_peers.append(peer)
                with peer.status_lock:
                    peer.status.am_choking = False
    
    def remove_unchoked_peer(self, peer):
        with self.unchoked_peers_lock:
            if peer in self.unchoked_peers:
                self.unchoked_peers.remove(peer)
                with peer.status_lock:
                    peer.status.am_choking = True
             
    
    #status
    def set_peer_choking(self, peer_id):
        try:
            peer = self.get_peer(peer_id)
        except Exception as e:
            logging.error(f"Unexpected error in set_peer_choking: {e}")
        if peer:
            with peer.status_lock:
                peer.status.peer_choking = True

    def reset_peer_choking(self, peer_id):
        peer = self.get_peer(peer_id)
        if peer:
            with peer.status_lock:
                peer.status.peer_choking = False
    # bit field

    def update_index_bitfield(self, peer, pieces_left, list_bitfield):
        with self.index_bitfield_lock:
            peer.pieces_left = pieces_left
            peer.index_bitfield.update({
                i: 1 for i, bit in enumerate(list_bitfield) if bit == "1"
            })
    
    # get peers pieces

    def get_all_peers(self):
        return self.active_peers

    def get_peer(self, id):
        found_peers = [peer for peer in self.active_peers if peer.id == id]
        return found_peers[0] if found_peers else None

    
    def get_peers_with_piece(self, index):
        try:
            return [peer for peer in self.active_peers if peer.index_bitfield[index] == 1]
        except Exception as e:
            pass
    
    def get_pieces_for_peer(self, peer):
        return [index for index, bitfield in peer.index_bitfield.items() if bitfield == 0]
    
    # unchoked peers

    def get_unchoked_peers(self):
        with self.unchoked_peers_lock:
            return self.unchoked_peers
    
    def remove_unchoked_peers(self,peer):
        with self.unchoked_peers_lock:
            if peer in self.unchoked_peers:
                self.unchoked_peers.remove(peer)

    # interested list
    def set_intersted(self, peer):
        with peer.status_lock:
            peer.status.interested = True

    def get_interested_peers(self):
        with self.active_peers_lock:    
                return list(peer for peer in self.active_peers if peer.status.interested == True)

    #choke and unchoke

    def check_and_choke(self, sock, peer):
        try:
            with peer.status_lock:
                peer.status.am_choking = True
            with self.unchoked_peers_lock:
                if peer not in self.unchoked_peers:
                    logging.warning("Peer is choked but try to send_choked")
                else:
                    self.unchoked_peers.remove(peer)
                    with peer.status_lock:
                        peer.status.am_choking = True
            raw_msg = {
                "opcode": "CHOKED",
                "peer_id": self.id
            }

            choke_msg = encode_choked(raw_msg)
            send_msg(sock, choke_msg)
        except Exception as e:
            logging.error(f"Unexpected error in check_and_choke: {e}")
            raise

    def check_and_unchoke(self, sock, peer):
        with peer.status_lock:
            peer.status.am_choking = False
        with self.unchoked_peers_lock:
            if peer in self.unchoked_peers:
                logging.warning("Peer is unchoked but try to send_unchoked")
            else:
                self.unchoked_peers.append(peer)
                with peer.status_lock:
                    peer.status.am_choking = False
        raw_msg = {
            "opcode": "UNCHOKED",
            "peer_id": self.id
        }
        unchoke_msg = encode_unchoked(raw_msg)
        send_msg(sock, unchoke_msg)
        logging.info("Sent Unchoked")
    
    def send_choked(self, sock, peer):
        choke_msg = encode_choked(None)
        send_msg(sock,choke_msg)
        Peer_manager.remove_unchoked_peer(peer)

    def send_unchoked(self, sock, peer):
        unchoke_msg = encode_unchoked(None)
        send_msg(sock,unchoke_msg)
        Peer_manager.remove_unchoked_peer(peer)