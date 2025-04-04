class Peer:
    def __init__(self, ip, port, list_pieces):
        self.ip = ip
        self.port = port
        self.pieces_left = list_pieces
        self.state = 'leecher' if self.pieces_left else 'seeder'

class PeerFactory:
    @staticmethod
    def new_peer(ip, port, list_pieces):
        return Peer(ip, port, list_pieces)