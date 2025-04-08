from state.choke_strategy_state import ChokeStrategyState

class LeecherChokeStrategy(ChokeStrategyState):
    def select_peers_to_unchoke(self, peer_manager):
        peers = peer_manager.get_interested_peers()
        sorted_peers = sorted(peers, key=lambda p: p.download_speed, reverse=True)
        return sorted_peers[:4]  # top 4 download speed
