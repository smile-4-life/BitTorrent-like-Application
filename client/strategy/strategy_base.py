from abc import ABC, abstractmethod

class PieceSelectionStrategy(ABC):
    @abstractmethod
    def select_pieces(self, strategy_manager, piece_manager, peer_manager):
        pass