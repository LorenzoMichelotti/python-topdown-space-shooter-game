from abc import ABC, abstractmethod


class Scene(ABC):
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def render(self, dt: float):
        pass
