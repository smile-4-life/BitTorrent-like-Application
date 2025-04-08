import random
from state.choke_strategy_state import ChokeStrategyState

class SeederState(ChokeStrategyState):
    def select_peers_to_unchoke(self, peer_manager):
        peers = peer_manager.get_interested_peers()
        if not peers:
            return []
        return random.sample(peers, min(len(peers), 2))  # unchoke 2 random peers
