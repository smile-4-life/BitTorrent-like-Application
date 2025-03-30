import logging

from enum import Enum 
from abc import ABC, abstractmethod

from connection.tracker_client_connection import *

class ClientState(Enum):
    IDLE = "Idle"
    CONNECTING_TRACKER = "Connecting"

class State(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def connect_to_tracker(self):
        pass

    @abstractmethod
    def seeding(self):
        pass

class IdleState(State):
    def connect_to_tracker(self):
        logging.info("IdleState: connecting to tracker")
        self.connection = ClientTracker(self.client)
        self.connection.register()
        self.client.change_state(ConnectingTrackerState(self.client))
    def seeding(self):
        pass

class ConnectingTrackerState(State):
    def connect_to_tracker(self):
        pass
    def seeding(self):
        self.client.change_state(SeedingState(self.client))
    
class SeedingState(State):
    def connect_to_tracker(self):
        pass
    def seeding(self):
        pass