from state.leecher_choke import LeecherState
from state.seeder_choke import SeederState
from protocol.peer_protocol import *
from handler.choking_handler import HandleChoking
from handler.piece_handler import HandlePiece
import logging

class ChokeManager:
    def __init__(self, state, id):
        self.state = state
        self.peer_id = id

    def set_state(self, state):
        self.state = state

    def run_choking_cycle(self, Peer_manager, Peer_connection):
        """Execute the choking algorithm to optimize peer connections."""
        try:
            # 1. Select peers to unchoke based on current strategy
            selected_peers = self.state.select_peers_to_unchoke(Peer_manager)
            if not selected_peers:
                logging.warning("No peers selected for unchoking")
                return

            # 2. Get currently unchoked peers
            unchoked_peers = set(Peer_manager.get_unchoked_peers())  # Convert to set for faster lookups
            new_unchokes = []
            already_unchoked = []

            # 3. Process peers that need to be unchoked
            for peer in selected_peers:
                if peer not in unchoked_peers:
                    try:
                        self._unchoke(peer, Peer_connection, Peer_manager)
                        Peer_manager.unchoked_peers.append(peer)
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
                    Peer_manager.remove_unchoked_peers(peer)
                    self._choke(peer, Peer_connection)
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

    
    def _unchoke(self, peer, Peer_connection, Peer_manager):
        if peer in Peer_manager.unchoked_peers:
            return
        #else
        
        raw_msg = {
            "opcode": "UNCHOKED",
            "peer_id": self.peer_id
        }
        unchoke_msg = encode_unchoked(raw_msg)
        send_msg(peer.sock,unchoke_msg)
        Peer_manager.add_unchoked_peer(peer)

    def _choke(self, peer, Peer_connection, Peer_manager):
        if peer not in Peer_manager.unchoked_peers:
            return
        #else
        
        raw_msg = {
            "opcode": "CHOKED",
            "peer_id": self.peer_id
        }
        choke_msg = encode_choked(raw_msg)
        send_msg(peer.sock,choke_msg)
        Peer_manager.remove_unchoked_peer(peer)
        
