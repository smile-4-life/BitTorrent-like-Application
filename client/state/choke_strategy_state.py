from abc import ABC, abstractmethod

class ChokeStrategyState(ABC):
    @abstractmethod
    def select_peers_to_unchoke(self, peer_manager):
        pass
