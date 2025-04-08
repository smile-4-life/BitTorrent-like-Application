import random

from strategy.strategy_base import PieceSelectionStrategy
from strategy.random_strategy import RandomStrategy

class RarestFirstStrategy(PieceSelectionStrategy):
    def select_pieces(self, strategy_manager, piece_manager, peer_manager):
        # Dictionary to track piece rarity (how many peers have each piece)
        piece_rarity = {}
        piece_to_peers = {}

        # Analyze all missing pieces
        for piece in piece_manager.get_missing_pieces():
            peers_with_piece = peer_manager.get_peers_with_piece(piece)
            if peers_with_piece:
                peer_num = len(peers_with_piece)
                if peer_num <= max(2, len(peer_manager.active_peers) / 2):
                    piece_rarity[piece] = peer_num
                    piece_to_peers[piece] = peers_with_piece

        if not piece_to_peers:
            strategy_manager.set_strategy(RandomStrategy())
            return strategy_manager.strategy.select_pieces(strategy_manager, piece_manager, peer_manager)

        # Sort pieces by rarity (rarest first)
        rarest_pieces = sorted(piece_rarity.keys(), key=lambda p: piece_rarity[p])

        # Select peers for each piece
        piece_assignments = {}
        
        for piece in rarest_pieces:
            # Get peers that have this piece
            available_peers = piece_to_peers[piece]
            
            # Sort peers by download speed (fastest first)
            sorted_peers = sorted(
                available_peers,
                key=lambda peer: peer.download_speed,
                reverse=True
            )
            
            # Take top 2 fastest peers
            top_two_peers = sorted_peers[:2]
            
            # Randomly select 1 peer from the top 2
            selected_peer = random.choice(top_two_peers)
            
            # Assign the piece to this peer
            if selected_peer not in piece_assignments:
                piece_assignments[selected_peer] = []
            piece_assignments[selected_peer].append(piece)

        return piece_assignments