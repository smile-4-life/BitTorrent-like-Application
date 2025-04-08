class PriorityBasedStrategy(PieceSelectionStrategy):
    def select_pieces(self, strategy_manager, piece_manager, peer_manager):
        total = len(available_pieces)
        priority_count = int(total * 0.05)
        priority_pieces = [i for i in range(priority_count) if i not in downloaded_pieces]

        return self._assign_pieces_to_peers(priority_pieces, peer_bitfields)
