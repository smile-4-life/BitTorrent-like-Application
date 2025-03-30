import logging
import threading

class TrackerSubject:
    def __init__(self):
        self.peers = {}
        self.data_lock = threading.Lock()

    def register_peer(self, peer_addr):
        with self.data_lock:
            if peer_addr not in self.peers:
                self.peers[peer_addr] = []
                logging.info(f"✅ Registered peer: {peer_addr}")
                return True
            logging.warning(f"⚠️ Peer already registered: {peer_addr}")
            return False

    def update_piece(self, peer_addr, hash_value):
        with self.data_lock:
            if peer_addr in self.peers:
                self.peers[peer_addr].append(hash_value)
                logging.info(f"🔄 Updated downloaded hash {hash_value} from peer {peer_addr}.")

    def get_peers(self):
        with self.data_lock:
            return self.peers.copy()

    def unregister_peer(self, peer_addr):
        with self.data_lock:
            if peer_addr in self.peers:
                del self.peers[peer_addr]
                logging.info(f"❌ Unregistered peer: {peer_addr}")
