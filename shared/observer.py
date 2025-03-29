from abc import ABC, abstractmethod

class Subject(ABC):
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self, data):
        for observer in self._observers:
            observer.update(data)

class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass