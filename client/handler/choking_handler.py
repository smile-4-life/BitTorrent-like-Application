import threading
import time
import logging

from state.leecher_choke import LeecherState
from state.seeder_choke import SeederState

class HandleChoking():
    def __init__(self, Peer_manager):
        self.Peer_manager = Peer_manager


    # ===== CHOKED =====
    def handle_choked(self, sock, msg):
        self.Peer_manager.set_peer_choking(msg.get("peer_id"))

    def handle_unchoked(self, sock, msg):
        self.Peer_manager.reset_peer_choking(msg.get("peer_id"))