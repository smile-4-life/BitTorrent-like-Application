class InterestedHandler:
    def __init__(self, peer_manager, piece_manager, peer_connection):
        self.peer_manager = peer_manager
        self.piece_manager = piece_manager
        self.peer_connection = peer_connection

    def handle_interested(self, sock, peer_ip, msg):
        try:
            peer_id = msg.get("peer_id")
            peer_port = msg.get("peer_port")
            peer = self.Peer_manager.get_peer(peer_id)
            if peer:
                self.Peer_manager.set_intersted(peer)

            if not self._check_and_choke(sock,peer):
                return

            while True:
                msg = self.Peer_connection.receive_message(sock)
            
                if msg.get("opcode") == "REQUEST":
                    peer_id = msg.get("peer_id")
                    peer = self.Peer_manager.get_peer(peer_id)
                    if peer:
                        if peer.status.am_choking == True:
                            self.Peer_manager.send_choked(sock, peer)
                            logging.info(f"Choke peer {peer_id} while being requested")
                            return
                    else:
                        logging.error(f"Cant found peer {peer_id}")
                        return
                    piece_index = msg.get("piece_index")
                    piece = self.Piece_manager.load_piece(piece_index)
                    raw_msg = {
                        "opcode": "PIECE",
                        "piece": piece,
                        "piece_index": piece_index
                    }
                    bi_msg = encode_piece(raw_msg)
                    send_msg(sock, bi_msg)
                    logging.info("Sent piece to {peer_ip}:{peer_port}")
                
                elif msg.get("opcode") == "DONE":
                    return
                
                else:
                    logging.warning(f"Unexpected Opcode: {msg}")
                    return
        except Exception as e:
            logging.error(f"Unexpected error in _handle_interested: {e}")
        finally:
            sock.close()
            logging.warning("Closing socket in interested")

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