import threading
import time
import logging

from state.leecher_choke import LeecherState
from state.seeder_choke import SeederState

class Choking():
    def __init__(self, id, port, Piece_manager, Peer_manager, Peer_connection, Choke_manager):
        self.id = id
        self.port = port
        self.Piece_manager = Piece_manager
        self.Peer_manager = Peer_manager
        self.Peer_connection = Peer_connection

        self.Choke_manager = Choke_manager 

    # ===== CHOKING LOOP =====
    def start_loop_choking (self):
        choking_thread = threading.Thread(target=self._loop_choking)
        choking_thread.daemon = True
        choking_thread.start()

    def _loop_choking(self):
        while True:
            if self.Piece_manager.pieces_left == 0:
                self.Choke_manager.set_state(SeederState())
            self.Choke_manager.run_choking_cycle(self.Peer_manager, self.Peer_connection)
            time.sleep(10) 