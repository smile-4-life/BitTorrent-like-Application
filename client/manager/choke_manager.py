from state.leecher_choke import LeecherState
from state.seeder_choke import SeederState
from protocol.peer_protocol import *
import logging

class ChokeManager:
    def __init__(self, state):
        self.state = state

    def set_state(self, state):
        self.state = state

    def run_choking_cycle(self, peer_manager, peer_connection):
        """Execute the choking algorithm to optimize peer connections."""
        try:
            # 1. Select peers to unchoke based on current strategy
            selected_peers = self.state.select_peers_to_unchoke(peer_manager)
            if not selected_peers:
                logging.warning("No peers selected for unchoking")
                return

            # 2. Get currently unchoked peers
            unchoked_peers = set(peer_manager.get_unchoked_peers())  # Convert to set for faster lookups
            new_unchokes = []
            already_unchoked = []

            # 3. Process peers that need to be unchoked
            for peer in selected_peers:
                if peer not in unchoked_peers:
                    try:
                        self._unchoke(peer, peer_connection)
                        peer_manager.unchoked_peers.append(peer)
                        new_unchokes.append(peer)
                    except Exception as e:
                        logging.error(f"Failed to unchoke peer {peer}: {str(e)}")
                else:
                    already_unchoked.append(peer)

            # 4. Identify peers that need to be choked
            peers_to_choke = unchoked_peers - set(selected_peers)
            
            # 5. Process choking
            for peer in peers_to_choke:
                try:
                    peer_manager.remove_unchoked_peers(peer)
                    self._choke(peer, peer_connection)
                    logging.debug(f"Choked peer {peer}")
                except Exception as e:
                    logging.error(f"Failed to choke peer {peer}: {str(e)}")

            # Logging summary
            logging.info(
                f"Choking cycle complete. "
                f"New unchokes: {len(new_unchokes)}, "
                f"Maintained unchokes: {len(already_unchoked)}, "
                f"New chokes: {len(peers_to_choke)}"
            )

        except Exception as e:
            logging.error(f"Error in choking cycle: {str(e)}", exc_info=True)

    
    def _unchoke(self, peer, Peer_connection):
        sock = Peer_connection.connect_to_peer(peer)
        unchoke_msg = encode_unchoked()
        send_msg(sock,unchoke_msg)

    def _choke(self, peer, Peer_connection):
        sock = Peer_connection.connect_to_peer(peer)
        choke_msg = encode_choked({})
        send_msg(sock, choke_msg)
            
        
