class BaseHandler:
    def handle(self, sock, peer_ip, msg):
        raise NotImplementedError

class HandshakeHandler(BaseHandler):
    def __init__(self, handshake_module):
        self.handler = handshake_module

    def handle(self, sock, peer_ip, msg):
        self.handler.handle_handshake(sock, peer_ip, msg)

class InterestedHandler(BaseHandler):
    def __init__(self, interested_handler):
        self.handler = interested_handler

    def handle(self, sock, peer_ip, msg):
        self.handler.handle_interested(sock, peer_ip, msg)

class ChokedHandler(BaseHandler):
    def __init__(self, choking_handler):
        self.handler = choking_handler

    def handle(self, sock, msg):
        self.handler.handle_choked(sock, msg)

class UnchokedHandler(BaseHandler):
    def __init__(self, choking_handler):
        self.handler = choking_handler

    def handle(self, sock, msg):
        self.handler.handle_unchoked(sock, msg)

class RequestHandler(BaseHandler):
    def __init__(self, request_handler):
        self.handler = request_handler

    def handle(self, sock, peer_ip, msg):
        self.handler.handle_request(sock, peer_ip, msg)

class PieceHandler(BaseHandler):
    def __init__(self, piece_handler):
        self.handler = piece_handler

    def handle(self, sock, msg):
        self.handler.handle_piece(sock, msg)
