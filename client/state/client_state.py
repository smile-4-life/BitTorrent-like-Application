import logging

from enum import Enum 
from abc import ABC, abstractmethod

from protocol.peer_protocol import *

''''''
class State(ABC):
    def __init__(self, client_observer):
        self.client_observer = client_observer


    @abstractmethod
    def seeding(self):
        pass
    
    @abstractmethod
    def leeching(self):
        pass

''''''

class LeechingState(State):
    def seeding(self):
        pass
    def leeching(self):
        pass


class SeedingState(State):
    def seeding(self):
        pass
    def leeching(self):
        pass