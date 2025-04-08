class ChokeManager:
    def __init__(self, strategy):
        self.strategy = strategy

    def set_strategy(self, strategy):
        self.strategy = strategy

    def run_choking_cycle(self, peer_manager):
        selected_peers = self.strategy.select_peers_to_unchoke(peer_manager)

        for peer in peer_manager.get_all_peers():
            if peer in selected_peers:
                peer.unchoke()
            else:
                peer.choke()
