class PeerState:
    def __init__(self):
        self.download_speed = 0
        self.am_choking = True
        self.peer_choking = True

class PeerManager:
    def __init__(self):
        self.peers = {}  # {Peer: PeerState}

    def add_peer(self, peer):
        if peer not in self.peers:
            self.peers[peer] = PeerState()

    def remove_peer(self, peer):
        if peer in self.peers:
            del self.peers[peer]

    def get_all_peers(self):
        return list(self.peers.keys())

    def has_peer(self, peer):
        return peer in self.peers

    def get_peer(self, ip, port):
        for peer in self.peers:
            if peer.ip == ip and peer.port == port:
                return peer
        return None

    def get_peer_state(self, peer):
        return self.peers.get(peer)

    def get_peers_by_download_speed(self):
        return sorted(self.peers.items(), key=lambda item: item[1].download_speed, reverse=True)

    def get_am_choking_peers(self):
        return [peer for peer, state in self.peers.items() if state.am_choking]

    def update_download_speed(self, peer, new_sample, alpha=0.2):
        if peer in self.peers:
            current_speed = self.peers[peer].download_speed
            updated_speed = (1 - alpha) * current_speed + alpha * new_sample
            self.peers[peer].download_speed = updated_speed