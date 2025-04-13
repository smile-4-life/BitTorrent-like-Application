import logging

class HandlePiece():
    def __init__(self, Piece_manager):
        self.Piece_manager = Piece_manager
    
    def handle_piece(self, sock, msg):
        piece = msg.get("piece")
        piece_index = msg.get("piece_index")
        self.Piece_manager.down_piece(piece_index, piece)