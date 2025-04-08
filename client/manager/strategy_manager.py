from strategy.rarestfirst_strategy import RarestFirstStrategy

class StrategyManager:
    def __init__(self):
        self.strategy = RarestFirstStrategy()

    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def select_pieces(self, piece_manager, peer_manager):
        return self.strategy.select_pieces(self, piece_manager, peer_manager)