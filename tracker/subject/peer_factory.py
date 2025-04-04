class Peer:
    def __init__(self, ip, port, pieces_left):
        self.ip = ip
        self.port = port
        self.pieces_left = pieces_left
        self.state = 'leecher' if self.pieces_left else 'seeder'

class PeerFactory:
    @staticmethod
    def new_peer(ip, port, pieces_left):
        return Peer(ip, port, pieces_left)