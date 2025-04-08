class EndGameStrategy(PieceSelectionStrategy):
    def select_pieces(self, strategy_manager, piece_manager, peer_manager):
        remaining = [i for i in available_pieces if i not in downloaded_pieces]
        return self._assign_pieces_multiple_peers(remaining, peer_bitfields)
