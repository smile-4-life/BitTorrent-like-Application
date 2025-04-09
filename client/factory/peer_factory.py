class PeerStatus:
    def __init__(self):
        self.download_speed = 0
        self.am_choking = True
        self.peer_choking = True
        self.interested = False


class Peer:
    def __init__(self,id, addr):
        self.id = id
        self.ip = addr[0]
        self.port = addr[1]
        self.status = PeerStatus()
        self.index_bitfield = {}
        
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
    def new_peer(id, addr):
        return Peer(id, addr)