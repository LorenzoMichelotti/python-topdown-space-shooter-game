import pygame
from abc import ABC, abstractmethod
from entities.entity import Entity


class Static(Entity, ABC):
    screen: pygame.Surface
    pos: pygame.Vector2
    height: int = 10
    layer = 1  # Rendering layer
    shadow_layer = 0  # All shadows render below actors

    def __init__(
        self,
        screen: pygame.Surface,
        initial_pos: pygame.Vector2 = None,
    ):
        super().__init__()
        self.screen = screen
        self.pos = (
            initial_pos
            if initial_pos
            else pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        )

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def draw_shadow(self):
        pass

    @abstractmethod
    def move(self, dt: float):
        pass

    def update(self, dt: float):
        self.draw_shadow()  # Draw shadow first
        self.draw()  # Then draw actor on top
        self.move(dt)
