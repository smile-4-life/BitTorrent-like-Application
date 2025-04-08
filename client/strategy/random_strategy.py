import random

from strategy.strategy_base import PieceSelectionStrategy

class RandomStrategy(PieceSelectionStrategy):
    def select_pieces(self, strategy_manager, piece_manager, peer_manager):
        piece_assignments = {}
        missing_pieces = piece_manager.get_missing_pieces()
        
        if not missing_pieces:
            return piece_assignments  # No pieces needed
        
        # Create a list of all peers that have at least one missing piece
        eligible_peers = []
        for peer in peer_manager.active_peers:
            peer_pieces = peer_manager.get_pieces_for_peer(peer)
            if any(piece in missing_pieces for piece in peer_pieces):
                eligible_peers.append(peer)
        '''        
        if not eligible_peers:
            # Fallback to another strategy if no peers have needed pieces
            strategy_manager.set_strategy(RarestFirstStrategy)
            return strategy_manager.select_pieces(piece_manager, peer_manager)
        '''
        # Assign random pieces to random peers
        for piece in missing_pieces:
            # Get all peers that have this piece
            peers_with_piece = peer_manager.get_peers_with_piece(piece)
            if not peers_with_piece:
                continue
                
            # Select a random peer that has this piece
            selected_peer = random.choice(peers_with_piece)
            
            # Assign piece to peer
            if selected_peer not in piece_assignments:
                piece_assignments[selected_peer] = []
            piece_assignments[selected_peer].append(piece)
            
            '''
            # Optional: Limit number of pieces per peer
            if len(piece_assignments[selected_peer]) >= 3:  # Max 3 pieces per peer
                # Remove peer from future consideration
                eligible_peers = [p for p in eligible_peers if p != selected_peer]
            '''  
        return piece_assignments