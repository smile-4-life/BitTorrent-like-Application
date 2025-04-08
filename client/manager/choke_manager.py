from state.leecher_choke import LeecherState
from state.seeder_choke import SeederState
from protocol.peer_protocol import *

class ChokeManager:
    def __init__(self, state):
        self.state = state

    def set_state(self, state):
        self.state = state

    def run_choking_cycle(self, Peer_manager, Peer_connection):
        selected_peers = self.state.select_peers_to_unchoke(Peer_manager)
        print("run_choking_cycle")
        for peer in Peer_manager.get_all_peers():
            if peer in selected_peers:
                self._unchoke(peer, Peer_connection)
            else:
                self._choke(peer, Peer_connection)
    
    def _unchoke(self, peer, Peer_connection):
        sock = Peer_connection.connect_to_peer(peer)
        unchoke_msg = encode_unchoked()
        send_msg(sock,unchoke_msg)

    def _choke(self, peer, Peer_connection):
        try:
            sock = Peer_connection.connect_to_peer(peer)
        except Exception as e:
            print(f"ERROR 1: {e}")
        try:
            choke_msg = encode_choked({})
        except Exception as e:
            print(f"ERROR 2: {e}")

        try:
            send_msg(sock, choke_msg)

        except Exception as e:
            print(f"ERROR 3: {e}")
            
        
