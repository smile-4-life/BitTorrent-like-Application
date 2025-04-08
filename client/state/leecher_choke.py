from state.choke_strategy_state import ChokeStrategyState

class LeecherState(ChokeStrategyState):
    '''
    def select_peers_to_unchoke(self, Peer_manager):
        peers = Peer_manager.get_interested_peers()
        sorted_peers = sorted(peers, key=lambda p: p.download_speed, reverse=True)
        return sorted_peers[:2]  # top 2 download speed
    '''
    def select_peers_to_unchoke(self, Peer_manager):
        return Peer_manager.active_peers    #for debug
