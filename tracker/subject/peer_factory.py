class Peer:
    def __init__(self, ip, port, pieces_left):
        self.ip = ip
        self.port = port
        self.pieces_left = pieces_left
        self.state = 'leecher' if self.pieces_left else 'seeder'

    def __eq__(self, other):
        if not isinstance(other, Peer):
            return False
        return self.ip == other.ip and self.port == other.port

    def __repr__(self):
        return f"Peer(ip={self.ip}, port={self.port})"
        
class PeerFactory:
    @staticmethod
    def new_peer(ip, port, pieces_left):
        return Peer(ip, port, pieces_left)