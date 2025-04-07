import threading

class PeerManager:
    def __init__(self):
        self.raw_addrs_lock = threading.Lock()
        self.active_addrs_lock = threading.Lock()
        self.active_peers_lock = threading.Lock()
        self.index_bitfield_lock = threading.Lock()

        self.raw_addrs = []     # [list of tuple (ip,port)]
        self.active_addrs = []
        self.active_peers = []  # [list of object]



    # raw
    def add_raw_addr(self, addr):
        if addr not in self.raw_addrs and addr not in self.active_addrs:
            with self.raw_addrs_lock:
                self.raw_addrs.append(addr)
    
    def remove_raw_addr(self, addr):
        if addr in self.raw_addrs:
            with self.raw_addrs_lock:
                self.raw_addrs.remove(addr)
            with self.active_addrs_lock:
                self.active_addrs.append(addr)
            

    # active
    def add_active_peer(self, peer):
        with self.active_peers_lock:
            if peer not in self.active_peers:
                self.active_peers.append(peer)
        
    # bit field
    def update_index_bitfield(self, peer, list_bitfield):
        with self.index_bitfield_lock:
            peer.index_bitfield.update({
                i: 1 for i, bit in enumerate(list_bitfield) if bit == 1
            })