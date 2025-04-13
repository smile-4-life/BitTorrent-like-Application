import threading

class PeerStatus:
    def __init__(self):
        self.download_speed = 0
        self.am_choking = True
        self.peer_choking = True
        self.interested = False


class Peer:
    def __init__(self,sock, id, addr):
        self.status_lock = threading.Lock()

        self.sock = sock
        self.id = id
        self.ip = addr[0]
        self.port = addr[1]
        self.status = PeerStatus()
        self.index_bitfield = {}
        self.pieces_left = None
        
        
    def __eq__(self, other):
        if not isinstance(other, Peer):
            return False
        return self.ip == other.ip and self.port == other.port

    def __repr__(self):
        return f"Peer(ip={self.ip}, port={self.port})"

    def __hash__(self):
        return hash(self.id)

class PeerFactory:
    @staticmethod
    def new_peer(sock, id, addr):
        return Peer(sock, id, addr)