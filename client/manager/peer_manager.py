import threading

class PeerManager:
    def __init__(self):
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

    # bit field
    def update_index_bitfield(self, peer, list_bitfield):
        with self.index_bitfield_lock:
            peer.index_bitfield.update({
                i: 1 for i, bit in enumerate(list_bitfield) if bit == 1
            })
    
    # get peers
    def get_all_peers(self):
        return self.active_peers
    
    def get_peers_with_piece(self, index):
        try:
            return [peer for peer in self.active_peers if peer.index_bitfield[index] == 1]
        except Exception as e:
            pass
    
    def get_pieces_for_peer(self, peer):
        return [index for index, bitfield in peer.index_bitfield.items() if bitfield == 0]

    # interested list
    def set_intersted(self, peer):
        peer.status.interested = True

    def get_interested_peers(self):
        return list(peer for peer in self.active_peers if peer.status.interested == True)

    #choke and unchoke
    def unchoke(self, sock, peer):
        peer.status.am_choking = False
        with unchoked_peers_lock:
            if peer in self.unchoked_peers:
                return
            else:
                self.unchoked_peers.append(peer)
        unchoke_msg = encode_unchoked()
        send_msg(sock, choke_msg)
    
    def choke(self, sock, peer):
        peer.status.am_choking = True
        with unchoked_peers_lock:
            if peer not in self.unchoked_peers:
                return
            else:
                self.unchoked_peers.remove(peer)
        choke_msg = encode_choked()
        send_msg(sock, choke_msg)
