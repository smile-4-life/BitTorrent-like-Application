class Peer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        
    def __eq__(self, other):
        if not isinstance(other, Peer):
            return False
        return self.ip == other.ip and self.port == other.port

    def __repr__(self):
        return f"Peer(ip={self.ip}, port={self.port})"

class PeerFactory:
    @staticmethod
    def new_peer(ip, port):
        return Peer(ip, port)