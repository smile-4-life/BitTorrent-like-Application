import random
from state.choke_strategy_state import ChokeStrategyState

class SeederChokeStrategy(ChokeStrategyState):
    def select_peers_to_unchoke(self, peer_manager):
        peers = peer_manager.get_interested_peers()
        if not peers:
            return []
        return random.sample(peers, min(len(peers), 4))  # unchoke 4 random peers
