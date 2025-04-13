import logging

class HandleInterested():
    def __init__(self, id, port, Piece_manager, Peer_manager, Peer_connection):
        self.id = id
        self.port = port
        self.Piece_manager = Piece_manager
        self.Peer_manager = Peer_manager
        self.Peer_connection = Peer_connection

    def handle_interested(self, sock, peer_ip, msg):
        try:
            peer_id = msg.get("peer_id")
            peer_port = msg.get("peer_port")
            peer = self.Peer_manager.get_peer(peer_id)
            if peer:
                self.Peer_manager.set_intersted(peer)

            if not self._check_and_choke(sock,peer):
                return

        except Exception as e:
            logging.error(f"Unexpected error in _handle_interested: {e}")

    def _check_and_choke(self, sock, peer):
        try:
            if peer.status.am_choking == True:
                if len(self.Peer_manager.unchoked_peers) <= 2:
                    self.Peer_manager.check_and_unchoke(sock, peer)
                    return True
                else:
                    self.Peer_manager.check_and_choke(sock, peer)
                    return False
            elif peer.status.am_choking == False:
                self.Peer_manager.check_and_unchoke(sock, peer)
                return True

        except Exception as e:
            logging.error(f"Unexpected error in check_and_choke: {e}")

            