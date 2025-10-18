from abc import ABC, abstractmethod

from tags.tags import Tag


class Entity(ABC):
    def __init__(self):
        self.tags = []
        self.entity_manager = None
        self.lifetime = -1

    @abstractmethod
    def update(self, dt: float):
        pass
