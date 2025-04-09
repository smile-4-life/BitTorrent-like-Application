import random
import logging
from state.choke_strategy_state import ChokeStrategyState

class SeederState(ChokeStrategyState):
    def select_peers_to_unchoke(self, Peer_manager):
        try:
            interested_peers = Peer_manager.get_interested_peers()
            
            if not interested_peers:
                logging.info("No interested peers available for unchoking")
                return []
                
            # Remove duplicate peers if any exist
            unique_peers = list({peer.id: peer for peer in interested_peers}.values())
            num_to_unchoke = min(len(unique_peers), 2)  
            
            selected = random.sample(unique_peers, num_to_unchoke)
            
            # Log selection for debugging
            peer_ids = [p.id for p in selected]
            logging.info(f"Selected peers to unchoke: {peer_ids}")
            
            return selected
            
        except ValueError as e:
            # Handle case where sample size > population
            logging.warning(f"Not enough peers for sampling: {str(e)}")
            return unique_peers
        except Exception as e:
            logging.error(f"Error in select_peers_to_unchoke: {str(e)}", exc_info=True)
            return []